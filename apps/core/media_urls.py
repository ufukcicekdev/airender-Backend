"""Build public URLs for uploaded files (local or Spaces)."""

from __future__ import annotations

from django.conf import settings


def public_media_url(file_field) -> str | None:
    if not file_field:
        return None
    url = file_field.url
    if url.startswith(("http://", "https://")):
        return url
    if getattr(settings, "USE_S3", False):
        base = settings.MEDIA_URL.rstrip("/")
        path = url.lstrip("/")
        if path.startswith("media/"):
            path = path[6:]
        return f"{base}/{path.lstrip('/')}"
    base = settings.BACKEND_PUBLIC_URL.rstrip("/")
    if url.startswith("/"):
        return f"{base}{url}"
    return f"{base}/{url}"
