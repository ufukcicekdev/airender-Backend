import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Workflow",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(default="Main Workflow", max_length=255)),
                ("graph", models.JSONField(default=dict)),
                ("version", models.PositiveIntegerField(default=1)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="workflows", to="projects.project")),
            ],
            options={"db_table": "workflows", "ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="WorkflowNode",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("node_id", models.CharField(max_length=64)),
                ("type", models.CharField(max_length=64)),
                ("position", models.JSONField(default=dict)),
                ("data", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("workflow", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="nodes", to="workflow.workflow")),
            ],
            options={"db_table": "workflow_nodes", "unique_together": {("workflow", "node_id")}},
        ),
        migrations.CreateModel(
            name="WorkflowConnection",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("edge_id", models.CharField(max_length=64)),
                ("source", models.CharField(max_length=64)),
                ("target", models.CharField(max_length=64)),
                ("source_handle", models.CharField(blank=True, max_length=64)),
                ("target_handle", models.CharField(blank=True, max_length=64)),
                ("data", models.JSONField(default=dict)),
                ("workflow", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="connections", to="workflow.workflow")),
            ],
            options={"db_table": "workflow_connections", "unique_together": {("workflow", "edge_id")}},
        ),
    ]
