from django.core.management.base import BaseCommand

from apps.auth_system.models import User
from apps.billing.bootstrap import ensure_billing_catalog, ensure_pricing_settings
from apps.billing.models import CreditPack, Plan, PricingSettings
from apps.billing.services import ensure_user_subscription, get_default_plan


class Command(BaseCommand):
    help = "Seed pricing settings, plans, credit packs, and user subscriptions"

    def handle(self, *args, **options):
        ensure_pricing_settings()
        PricingSettings.objects.filter(pk=1).update(
            plans_section_title="",
            plans_section_description="",
            monthly_toggle_label="",
            monthly_description="",
            yearly_toggle_label="",
            yearly_description="",
            yearly_discount_note="",
            credits_section_title="Buy credits",
            credits_section_description=(
                "Pay as you go — no subscription. Register for trial credits, then buy a pack "
                "whenever you need more. 100 credits for $4.99."
            ),
            credits_footer_note=(
                "New accounts receive a small trial credit balance on signup. "
                "Purchased credits never expire. Video and 4K use more credits per run."
            ),
        )

        ensure_billing_catalog()

        get_default_plan()

        count = 0
        for user in User.objects.all():
            ensure_user_subscription(user)
            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded pricing settings, "
                f"{Plan.objects.filter(is_active=True).count()} plans, "
                f"{CreditPack.objects.filter(is_active=True).count()} credit packs. "
                f"Subscriptions ensured for {count} users."
            )
        )
