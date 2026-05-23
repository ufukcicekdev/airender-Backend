"""Helpers for project list API and naming."""

from __future__ import annotations

from typing import Any

from apps.auth_system.models import User

from .models import Project


def default_project_name(user: User) -> str:
    base = "Untitled"
    names = set(
        Project.objects.filter(user=user, name__startswith=base).values_list(
            "name", flat=True
        )
    )
    if base not in names:
        return base
    n = 2
    while f"{base} {n}" in names:
        n += 1
    return f"{base} {n}"


def preview_url_from_graph(graph: dict[str, Any] | None) -> str | None:
    if not graph:
        return None
    for node in graph.get("nodes") or []:
        data = node.get("data") or {}
        for key in ("imageUrl", "videoUrl", "thumbnailUrl"):
            url = data.get(key)
            if isinstance(url, str) and url.startswith(("http://", "https://", "/")):
                return url
    return None


def node_count_from_graph(graph: dict[str, Any] | None) -> int:
    if not graph:
        return 0
    return len(graph.get("nodes") or [])
