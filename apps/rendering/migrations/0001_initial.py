import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("workflow", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RenderTask",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("status", models.CharField(choices=[("queued", "Queued"), ("processing", "Processing"), ("completed", "Completed"), ("failed", "Failed"), ("cancelled", "Cancelled")], default="queued", max_length=20)),
                ("progress", models.PositiveSmallIntegerField(default=0)),
                ("current_stage", models.CharField(blank=True, max_length=64)),
                ("node_statuses", models.JSONField(default=dict)),
                ("error_message", models.TextField(blank=True)),
                ("celery_task_id", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="render_tasks", to=settings.AUTH_USER_MODEL)),
                ("workflow", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="render_tasks", to="workflow.workflow")),
            ],
            options={"db_table": "render_tasks", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="GeneratedImage",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("image", models.ImageField(upload_to="renders/")),
                ("thumbnail", models.ImageField(blank=True, null=True, upload_to="previews/")),
                ("width", models.PositiveIntegerField(default=0)),
                ("height", models.PositiveIntegerField(default=0)),
                ("metadata", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("render_task", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="rendering.rendertask")),
            ],
            options={"db_table": "generated_images"},
        ),
    ]
