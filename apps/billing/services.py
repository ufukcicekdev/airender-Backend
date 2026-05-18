from datetime import timedelta

from django.utils import timezone

from apps.auth_system.models import User

from .models import BillingCycle, CreditPack, Plan, PricingSettings, SubscriptionStatus, UserSubscription


def get_default_plan() -> Plan:
    plan, _ = Plan.objects.get_or_create(
        slug="free",
        defaults={
            "name": "Free",
            "description": "Get started with basic rendering",
            "price_monthly": 0,
            "price_yearly": 0,
            "credits_monthly": 100,
            "features": ["100 credits / month", "Standard quality", "Community support"],
            "sort_order": 0,
        },
    )
    return plan


def ensure_user_subscription(user: User) -> UserSubscription:
    if hasattr(user, "subscription"):
        return user.subscription
    plan = get_default_plan()
    return UserSubscription.objects.create(
        user=user,
        plan=plan,
        status=SubscriptionStatus.ACTIVE,
        billing_cycle=BillingCycle.MONTHLY,
    )


def subscribe_user(user: User, plan_slug: str, billing_cycle: str = BillingCycle.MONTHLY) -> UserSubscription:
    plan = Plan.objects.get(slug=plan_slug, is_active=True)
    period_end = timezone.now() + (
        timedelta(days=365) if billing_cycle == BillingCycle.YEARLY else timedelta(days=30)
    )

    sub, _ = UserSubscription.objects.update_or_create(
        user=user,
        defaults={
            "plan": plan,
            "status": SubscriptionStatus.ACTIVE,
            "billing_cycle": billing_cycle,
            "started_at": timezone.now(),
            "current_period_end": period_end,
        },
    )

    user.credits = plan.credits_monthly
    user.save(update_fields=["credits"])

    return sub


def get_pricing_overview() -> dict:
    return {
        "settings": PricingSettings.load(),
        "plans": Plan.objects.filter(is_active=True),
        "credit_packs": CreditPack.objects.filter(is_active=True),
    }


def purchase_credit_pack(user: User, pack_slug: str) -> CreditPack:
    pack = CreditPack.objects.get(slug=pack_slug, is_active=True)
    user.credits += pack.total_credits
    user.save(update_fields=["credits"])
    return pack
