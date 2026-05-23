"""Object storage helpers (local media vs S3/Spaces)."""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


def use_s3_storage() -> bool:
    return bool(getattr(settings, "USE_S3", False))


def storage_backend_label() -> str:
    return default_storage.__class__.__name__


def assert_s3_ready() -> None:
    """Raise if USE_S3 is set but Django is not using S3 storage."""
    if not getattr(settings, "USE_S3", False):
        return
    name = storage_backend_label()
    if "S3" not in name:
        raise ImproperlyConfigured(
            f"USE_S3=1 but default storage is {name}. "
            "Check AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_STORAGE_BUCKET_NAME."
        )


def log_storage_status() -> None:
    if use_s3_storage():
        logger.info(
            "Media storage: %s → %s",
            storage_backend_label(),
            getattr(settings, "MEDIA_URL", ""),
        )
    else:
        logger.warning(
            "Media storage: local filesystem at %s (set USE_S3=1 for production)",
            getattr(settings, "MEDIA_ROOT", ""),
        )
