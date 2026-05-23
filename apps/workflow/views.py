from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.activity import record_project_activity
from apps.projects.models import Project

from .models import Workflow
from .serializers import WorkflowSaveSerializer, WorkflowSerializer


class WorkflowDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_workflow(self, request, workflow_id):
        return get_object_or_404(
            Workflow.objects.select_related("project"),
            id=workflow_id,
            project__user=request.user,
        )

    def get(self, request, workflow_id):
        workflow = self.get_workflow(request, workflow_id)
        return Response(WorkflowSerializer(workflow).data)

    def put(self, request, workflow_id):
        workflow = self.get_workflow(request, workflow_id)
        serializer = WorkflowSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        workflow.graph = serializer.validated_data["graph"]
        if "name" in serializer.validated_data:
            workflow.name = serializer.validated_data["name"]
        workflow.version += 1
        workflow.save(update_fields=["graph", "name", "version", "updated_at"])
        record_project_activity(workflow.project_id, "Canvas saved")
        return Response(WorkflowSerializer(workflow).data)

    def patch(self, request, workflow_id):
        return self.put(request, workflow_id)


class WorkflowByProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, user=request.user)
        workflow = project.workflows.first()
        if not workflow:
            workflow = Workflow.objects.create(
                project=project, name="Main Workflow", graph={"nodes": [], "edges": []}
            )
        return Response(WorkflowSerializer(workflow).data)


class WorkflowDuplicateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, workflow_id):
        source = get_object_or_404(
            Workflow, id=workflow_id, project__user=request.user
        )
        new_wf = Workflow.objects.create(
            project=source.project,
            name=f"{source.name} (copy)",
            graph=source.graph,
        )
        return Response(WorkflowSerializer(new_wf).data, status=status.HTTP_201_CREATED)


class WorkflowExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, workflow_id):
        workflow = get_object_or_404(
            Workflow, id=workflow_id, project__user=request.user
        )
        return Response(
            {
                "version": workflow.version,
                "name": workflow.name,
                "graph": workflow.graph,
                "exported_at": workflow.updated_at.isoformat(),
            }
        )


class WorkflowImportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, workflow_id):
        workflow = get_object_or_404(
            Workflow, id=workflow_id, project__user=request.user
        )
        serializer = WorkflowSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        workflow.graph = serializer.validated_data["graph"]
        workflow.version += 1
        workflow.save(update_fields=["graph", "version", "updated_at"])
        record_project_activity(workflow.project_id, "Canvas imported")
        return Response(WorkflowSerializer(workflow).data)
