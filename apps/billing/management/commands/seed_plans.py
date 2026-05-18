from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.auth_system.models import User
from apps.billing.models import CreditPack, Plan, PricingSettings
from apps.billing.services import ensure_user_subscription, get_default_plan


class Command(BaseCommand):
    help = "Seed pricing settings, plans, credit packs, and user subscriptions"

    def handle(self, *args, **options):
        PricingSettings.objects.update_or_create(
            pk=1,
            defaults={
                "plans_section_title": "Subscription plans",
                "plans_section_description": (
                    "Bill monthly or yearly. All paid plans include a monthly credit allowance "
                    "for renders in the node editor."
                ),
                "monthly_toggle_label": "Monthly",
                "monthly_description": (
                    "Flexible billing — pay each month. Ideal for trying Pro or Studio short-term."
                ),
                "yearly_toggle_label": "Yearly",
                "yearly_description": (
                    "Pay once per year and lock in a lower effective rate. Best for teams with "
                    "continuous production."
                ),
                "yearly_discount_note": "Save ~17% vs paying monthly",
                "credits_section_title": "Buy credits",
                "credits_section_description": (
                    "Need more renders this month? Purchase a credit pack — credits are added "
                    "instantly to your balance and never expire."
                ),
                "credits_footer_note": (
                    "Credit cost per render depends on the model you select (shown in the editor). "
                    "Plan credits reset each billing period; purchased packs stack on top."
                ),
            },
        )

        plans = [
            {
                "slug": "free",
                "name": "Free",
                "description": "Perfect for exploring Vizmake",
                "price_monthly": Decimal("0"),
                "price_yearly": Decimal("0"),
                "monthly_description": "No payment required. 100 credits refresh every month.",
                "yearly_description": "Stay on Free — same limits, no annual charge.",
                "credits_monthly": 100,
                "features": [
                    "100 credits / month",
                    "Standard render quality",
                    "1 active project",
                    "Community support",
                ],
                "is_popular": False,
                "sort_order": 0,
            },
            {
                "slug": "pro",
                "name": "Pro",
                "description": "For creators shipping work weekly",
                "price_monthly": Decimal("29"),
                "price_yearly": Decimal("290"),
                "monthly_description": "$29 billed every month. Cancel anytime from your account.",
                "yearly_description": "$290 billed once per year — equivalent to ~$24/mo.",
                "credits_monthly": 1000,
                "features": [
                    "1,000 credits / month",
                    "High quality renders",
                    "Unlimited projects",
                    "Priority queue",
                    "Email support",
                ],
                "is_popular": True,
                "sort_order": 1,
            },
            {
                "slug": "studio",
                "name": "Studio",
                "description": "Teams and production pipelines",
                "price_monthly": Decimal("79"),
                "price_yearly": Decimal("790"),
                "monthly_description": "$79 billed every month. Full catalog + priority support.",
                "yearly_description": "$790 billed annually — equivalent to ~$66/mo for studios.",
                "credits_monthly": 5000,
                "features": [
                    "5,000 credits / month",
                    "Ultra quality + batch render",
                    "Unlimited projects",
                    "Dedicated support",
                    "API access",
                    "Custom workflows",
                ],
                "is_popular": False,
                "sort_order": 2,
            },
        ]

        for data in plans:
            Plan.objects.update_or_create(slug=data["slug"], defaults={**data, "is_active": True})

        credit_packs = [
            {
                "slug": "credits-500",
                "name": "Starter pack",
                "description": "A small top-up for a few extra renders",
                "credits": 500,
                "bonus_credits": 0,
                "price": Decimal("9"),
                "features": ["Never expires", "Stacks with plan credits"],
                "sort_order": 0,
            },
            {
                "slug": "credits-2000",
                "name": "Creator pack",
                "description": "Best value for solo artists mid-project",
                "credits": 2000,
                "bonus_credits": 200,
                "price": Decimal("29"),
                "features": ["+200 bonus credits", "Never expires", "Stacks with plan credits"],
                "is_popular": True,
                "sort_order": 1,
            },
            {
                "slug": "credits-10000",
                "name": "Studio pack",
                "description": "Bulk credits for teams and deadline weeks",
                "credits": 10000,
                "bonus_credits": 1500,
                "price": Decimal("99"),
                "features": [
                    "+1,500 bonus credits",
                    "Never expires",
                    "Priority processing",
                ],
                "sort_order": 2,
            },
        ]

        for data in credit_packs:
            CreditPack.objects.update_or_create(
                slug=data["slug"],
                defaults={**data, "is_active": True, "currency": "USD"},
            )

        get_default_plan()

        count = 0
        for user in User.objects.all():
            ensure_user_subscription(user)
            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded pricing settings, {len(plans)} plans, {len(credit_packs)} credit packs. "
                f"Subscriptions ensured for {count} users."
            )
        )
