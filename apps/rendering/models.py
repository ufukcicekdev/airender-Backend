import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class RenderTaskStatus(models.TextChoices):
    QUEUED = "queued", "Queued"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class RenderTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="render_tasks",
    )
    workflow = models.ForeignKey(
        "workflow.Workflow",
        on_delete=models.CASCADE,
        related_name="render_tasks",
    )
    status = models.CharField(
        max_length=20,
        choices=RenderTaskStatus.choices,
        default=RenderTaskStatus.QUEUED,
    )
    progress = models.PositiveSmallIntegerField(default=0)
    current_stage = models.CharField(max_length=64, blank=True)
    node_statuses = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "render_tasks"
        ordering = ["-created_at"]


class GeneratedImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    render_task = models.ForeignKey(
        RenderTask,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="renders/")
    thumbnail = models.ImageField(upload_to="previews/", blank=True, null=True)
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "generated_images"
