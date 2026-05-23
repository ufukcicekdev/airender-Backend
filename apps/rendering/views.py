import logging
import threading

from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.workflow.models import Workflow

from .models import RenderTask, RenderTaskStatus
from .providers import resolve_ai_model
from .render_context import credit_cost_for_render, get_render_node, validate_render_inputs
from .serializers import RenderTaskSerializer, StartRenderSerializer
from .tasks import run_render_pipeline

CANVAS_RENDER_TYPES = frozenset({"render", "detail"})

logger = logging.getLogger(__name__)


def _dispatch_render_task(task_id: str) -> None:
    """Queue render work without blocking the HTTP response."""
    from django.db import close_old_connections

    def _run() -> None:
        close_old_connections()
        try:
            run_render_pipeline.delay(task_id)
        except Exception:
            logger.exception("Background render failed task_id=%s", task_id)
            try:
                task = RenderTask.objects.get(id=task_id)
                if task.status not in (
                    RenderTaskStatus.COMPLETED,
                    RenderTaskStatus.FAILED,
                    RenderTaskStatus.CANCELLED,
                ):
                    task.status = RenderTaskStatus.FAILED
                    task.error_message = "Render worker error. Check backend logs."
                    task.save(update_fields=["status", "error_message"])
            except RenderTask.DoesNotExist:
                pass
        finally:
            close_old_connections()

    if settings.CELERY_TASK_ALWAYS_EAGER:
        threading.Thread(target=_run, daemon=True).start()
    else:
        run_render_pipeline.delay(task_id)


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
        graph = dict(workflow.graph or {})

        req_category = (serializer.validated_data.get("category_slug") or "").strip()
        req_model = (serializer.validated_data.get("model_slug") or "").strip()
        if node_id and (req_category or req_model):
            nodes = list(graph.get("nodes") or [])
            for node in nodes:
                if node.get("id") != node_id or node.get("type") not in CANVAS_RENDER_TYPES:
                    continue
                data = dict(node.get("data") or {})
                if req_category:
                    data["categorySlug"] = req_category
                if req_model:
                    data["modelSlug"] = req_model
                node["data"] = data
                break
            graph["nodes"] = nodes
            workflow.graph = graph
            workflow.save(update_fields=["graph", "updated_at"])

        render_node, _ = get_render_node(graph, node_id)
        if render_node:
            data = render_node.get("data") or {}
            cat = str(data.get("categorySlug") or "")
            slug = str(data.get("modelSlug") or "")
            if not cat or not slug:
                return Response(
                    {
                        "error": (
                            "Model not set on this generation node. "
                            "Pick a capability and engine in the right panel, then Make again."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            model = resolve_ai_model(cat, slug)
            if not model:
                return Response(
                    {
                        "error": f"Unknown model '{slug}' in category '{cat}'. Run: python manage.py seed_catalog",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            endpoint_path = (model.config or {}).get("endpoint_path", "")
            logger.info(
                "Render start user=%s model=%s/%s provider=%s endpoint=%s",
                request.user.email,
                cat,
                slug,
                model.provider,
                endpoint_path,
            )
            if model.provider != "fal":
                logger.warning(
                    "Model %s uses provider=%s (not fal). Check catalog seed.",
                    slug,
                    model.provider,
                )

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

        _dispatch_render_task(str(task.id))
        logger.info("Render queued task_id=%s node_id=%s", task.id, node_id)

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
