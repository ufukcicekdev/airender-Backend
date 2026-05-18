from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.workflow.models import Workflow
from apps.workflow.serializers import WorkflowSerializer

from .models import Project
from .serializers import ProjectListSerializer, ProjectSerializer


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

    def perform_create(self, serializer):
        project = serializer.save(user=self.request.user)
        Workflow.objects.create(project=project, name="Main Workflow", graph={"nodes": [], "edges": []})

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        source = self.get_object()
        new_project = Project.objects.create(
            user=request.user,
            name=f"{source.name} (copy)",
            description=source.description,
            is_template=False,
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
