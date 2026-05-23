"""Build public URLs for uploaded files (local or Spaces)."""

from __future__ import annotations

from django.conf import settings


def resolve_public_url_for_fal(url: str) -> str:
    """
    Fal must fetch source images from a public HTTPS URL (not /media proxy paths).
    """
    raw = (url or "").strip()
    if not raw:
        return ""

    # Strip accidental whitespace inside URLs (breaks Fal validation)
    cleaned = "".join(raw.split()) if raw.startswith(("http://", "https://")) else raw

    if cleaned.startswith(("http://", "https://")):
        lower = cleaned.lower()
        if "localhost" in lower or "127.0.0.1" in lower:
            if "/media/" in cleaned:
                rel = cleaned.split("/media/", 1)[1].lstrip("/")
                if getattr(settings, "USE_S3", False):
                    base = str(settings.MEDIA_URL).rstrip("/")
                    return f"{base}/{rel}"
            raise ValueError(
                "Source image is not publicly reachable. Use S3/Spaces storage or set "
                "BACKEND_PUBLIC_URL to a public HTTPS host."
            )
        return cleaned

    if getattr(settings, "USE_S3", False):
        base = str(settings.MEDIA_URL).rstrip("/")
        rel = cleaned.lstrip("/")
        if rel.startswith("media/"):
            rel = rel[6:]
        return f"{base}/{rel.lstrip('/')}"

    base = settings.BACKEND_PUBLIC_URL.rstrip("/")
    if cleaned.startswith("/"):
        return f"{base}{cleaned}"
    return f"{base}/{cleaned}"


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
