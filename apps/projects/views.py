from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.rendering.models import RenderTask
from apps.workflow.models import Workflow
from apps.workflow.serializers import WorkflowSerializer

from .activity import record_project_activity
from .models import Project
from .serializers import ProjectListSerializer, ProjectSerializer
from .utils import default_project_name


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        qs = Project.objects.filter(user=self.request.user)
        if self.action == "list":
            return qs.prefetch_related(
                Prefetch("workflows", queryset=Workflow.objects.all()[:1], to_attr="_workflows")
            )
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        return ProjectSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == "list":
            context["preview_by_project"] = self._preview_urls_by_project()
        return context

    def _preview_urls_by_project(self) -> dict[str, str]:
        qs = self.filter_queryset(self.get_queryset())
        project_ids = list(qs.values_list("id", flat=True))
        if not project_ids:
            return {}
        previews: dict[str, str] = {}
        tasks = (
            RenderTask.objects.filter(
                workflow__project_id__in=project_ids,
                status="completed",
            )
            .select_related("workflow")
            .prefetch_related("images")
            .order_by("-completed_at", "-created_at")
        )
        for task in tasks:
            pid = str(task.workflow.project_id)
            if pid in previews:
                continue
            gen = task.images.order_by("-created_at").first()
            if gen and gen.image:
                try:
                    previews[pid] = gen.image.url
                except Exception:
                    pass
        return previews

    def perform_create(self, serializer):
        name = serializer.validated_data.get("name") or default_project_name(self.request.user)
        project = serializer.save(
            user=self.request.user,
            name=name,
            last_activity_summary="Project created",
        )
        Workflow.objects.create(project=project, name="Main Workflow", graph={"nodes": [], "edges": []})

    def perform_update(self, serializer):
        project = serializer.save()
        if "name" in serializer.validated_data:
            record_project_activity(project.id, "Renamed project")

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        source = self.get_object()
        new_project = Project.objects.create(
            user=request.user,
            name=f"{source.name} (copy)",
            description=source.description,
            is_template=False,
            last_activity_summary="Duplicated project",
        )
        source_wf = source.workflows.first()
        if source_wf:
            Workflow.objects.create(
                project=new_project,
                name=source_wf.name,
                graph=source_wf.graph,
            )
        return Response(ProjectSerializer(new_project).data, status=201)

    @action(detail=False, methods=["get"])
    def templates(self, request):
        qs = Project.objects.filter(is_template=True)
        serializer = ProjectListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        qs = self.get_queryset()[:10]
        serializer = ProjectListSerializer(qs, many=True)
        return Response(serializer.data)
