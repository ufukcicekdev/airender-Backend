import uuid

from django.conf import settings
from django.db import models


class Asset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    name = models.CharField(max_length=255, blank=True)
    file = models.ImageField(upload_to="uploads/")
    thumbnail = models.ImageField(upload_to="previews/", blank=True, null=True)
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)
    file_size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "assets"
        ordering = ["-created_at"]
