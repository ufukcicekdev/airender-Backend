"""Ensure capability categories + models exist (like billing bootstrap)."""

from __future__ import annotations

import logging

from django.core.management import call_command

from .models import CapabilityCategory

logger = logging.getLogger(__name__)


def ensure_catalog() -> bool:
    """
    If no active capabilities, run seed_catalog (idempotent).
    Returns True when seed was triggered.
    """
    if CapabilityCategory.objects.filter(is_active=True).exists():
        return False
    logger.info("Catalog empty — running seed_catalog")
    call_command("seed_catalog", verbosity=0)
    return True
