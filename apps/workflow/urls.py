from django.urls import path

from .views import (
    WorkflowByProjectView,
    WorkflowDetailView,
    WorkflowDuplicateView,
    WorkflowExportView,
    WorkflowImportView,
)

urlpatterns = [
    path("project/<uuid:project_id>", WorkflowByProjectView.as_view(), name="workflow-by-project"),
    path("<uuid:workflow_id>", WorkflowDetailView.as_view(), name="workflow-detail"),
    path("<uuid:workflow_id>/duplicate", WorkflowDuplicateView.as_view(), name="workflow-duplicate"),
    path("<uuid:workflow_id>/export", WorkflowExportView.as_view(), name="workflow-export"),
    path("<uuid:workflow_id>/import", WorkflowImportView.as_view(), name="workflow-import"),
]
