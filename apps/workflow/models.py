import uuid

from django.db import models
from django.utils import timezone


class Workflow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="workflows",
    )
    name = models.CharField(max_length=255, default="Main Workflow")
    # Canonical DAG payload (React Flow): {"nodes": [], "edges": []}
    graph = models.JSONField(default=dict)

    @property
    def flow_data(self) -> dict:
        """Alias used by graph executor / API docs."""
        return self.graph

    @flow_data.setter
    def flow_data(self, value: dict) -> None:
        self.graph = value
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workflows"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.project.name} — {self.name}"


class WorkflowNode(models.Model):
    """Normalized node storage (optional; primary graph lives in Workflow.graph)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="nodes")
    node_id = models.CharField(max_length=64)  # React Flow id
    type = models.CharField(max_length=64)
    position = models.JSONField(default=dict)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "workflow_nodes"
        unique_together = ("workflow", "node_id")


class WorkflowConnection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="connections")
    edge_id = models.CharField(max_length=64)
    source = models.CharField(max_length=64)
    target = models.CharField(max_length=64)
    source_handle = models.CharField(max_length=64, blank=True)
    target_handle = models.CharField(max_length=64, blank=True)
    data = models.JSONField(default=dict)

    class Meta:
        db_table = "workflow_connections"
        unique_together = ("workflow", "edge_id")
