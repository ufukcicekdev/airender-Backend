from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.workflow.models import Workflow

from .models import RenderTask, RenderTaskStatus
from .render_context import credit_cost_for_render, validate_render_inputs
from .serializers import RenderTaskSerializer, StartRenderSerializer
from .tasks import run_render_pipeline


class StartRenderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StartRenderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workflow = get_object_or_404(
            Workflow,
            id=serializer.validated_data["workflow_id"],
            project__user=request.user,
        )

        node_id = (serializer.validated_data.get("node_id") or "").strip() or None
        graph = workflow.graph or {}

        input_error = validate_render_inputs(graph, node_id)
        if input_error:
            return Response({"error": input_error}, status=status.HTTP_400_BAD_REQUEST)

        credit_cost = credit_cost_for_render(graph, node_id)

        if request.user.credits < credit_cost:
            return Response(
                {
                    "error": "Insufficient credits.",
                    "required": credit_cost,
                    "available": request.user.credits,
                },
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        task = RenderTask.objects.create(
            user=request.user,
            workflow=workflow,
            status=RenderTaskStatus.QUEUED,
            node_statuses={"_target_render_id": node_id or ""} if node_id else {},
        )

        request.user.credits -= credit_cost
        request.user.save(update_fields=["credits"])

        run_render_pipeline.delay(str(task.id))

        return Response(RenderTaskSerializer(task, context={"request": request}).data, status=201)


class RenderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = get_object_or_404(RenderTask, id=task_id, user=request.user)
        return Response(RenderTaskSerializer(task, context={"request": request}).data)


class CancelRenderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        task = get_object_or_404(RenderTask, id=task_id, user=request.user)
        if task.status in (RenderTaskStatus.COMPLETED, RenderTaskStatus.FAILED):
            return Response({"error": "Task already finished."}, status=400)
        task.status = RenderTaskStatus.CANCELLED
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at"])
        return Response(RenderTaskSerializer(task, context={"request": request}).data)


class RenderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = RenderTask.objects.filter(user=request.user)[:20]
        return Response(
            RenderTaskSerializer(tasks, many=True, context={"request": request}).data
        )


class RenderPreviewView(APIView):
    """Latest generated file for a render task (image or video)."""

    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = get_object_or_404(RenderTask, id=task_id, user=request.user)
        gen = task.images.order_by("-created_at").first()
        if not gen or not gen.image:
            raise Http404("No output yet")
        content_type = "video/mp4" if gen.image.name.endswith(".mp4") else "image/png"
        return FileResponse(gen.image.open("rb"), content_type=content_type)
