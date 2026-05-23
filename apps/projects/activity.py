"""Update project last-activity line for dashboard."""

from __future__ import annotations

from django.utils import timezone

from .models import Project


def record_project_activity(project_id, summary: str) -> None:
    if not project_id or not summary:
        return
    Project.objects.filter(pk=project_id).update(
        last_activity_summary=str(summary)[:128],
        updated_at=timezone.now(),
    )
