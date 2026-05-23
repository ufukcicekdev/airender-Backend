"""Ensure billing catalog exists (plans + credit packs) on empty databases."""

from __future__ import annotations

import logging

from .catalog_defaults import (
    DEFAULT_CREDIT_PACKS,
    DEFAULT_PLANS,
    MEMBER_PLAN,
    RETIRED_CREDIT_PACK_SLUGS,
    RETIRED_PLAN_SLUGS,
)
from .models import CreditPack, Plan, PricingSettings, UserSubscription

logger = logging.getLogger(__name__)


def ensure_pricing_settings() -> PricingSettings:
    return PricingSettings.load()


def ensure_billing_catalog() -> None:
    """
    Upsert default plans and credit packs (idempotent).
    Called from pricing API so Account / landing always show packs.
    """
    ensure_pricing_settings()

    Plan.objects.update_or_create(
        slug=MEMBER_PLAN["slug"],
        defaults={**MEMBER_PLAN, "is_active": False, "currency": "USD"},
    )

    for data in DEFAULT_PLANS:
        Plan.objects.update_or_create(
            slug=data["slug"],
            defaults={**data, "is_active": True, "currency": "USD"},
        )

    Plan.objects.filter(slug__in=RETIRED_PLAN_SLUGS).update(is_active=False)

    for data in DEFAULT_CREDIT_PACKS:
        CreditPack.objects.update_or_create(
            slug=data["slug"],
            defaults={**data, "is_active": True, "currency": "USD"},
        )

    retired_packs = CreditPack.objects.filter(slug__in=RETIRED_CREDIT_PACK_SLUGS)
    if retired_packs.exists():
        retired_packs.update(is_active=False)

    member = Plan.objects.get(slug=MEMBER_PLAN["slug"])
    moved = UserSubscription.objects.filter(plan__slug__in=RETIRED_PLAN_SLUGS).update(plan=member)
    if moved:
        logger.info("Billing bootstrap: moved %s subscriptions to pay-as-you-go", moved)
