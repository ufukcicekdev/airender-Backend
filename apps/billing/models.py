import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class PricingSettings(models.Model):
    """Singleton: copy for pricing page (monthly/yearly toggles, credit shop)."""

    plans_section_title = models.CharField(max_length=200, default="Subscription plans")
    plans_section_description = models.TextField(
        blank=True,
        default="Choose monthly or yearly billing. Yearly plans include included credits each month.",
    )
    monthly_toggle_label = models.CharField(max_length=64, default="Monthly")
    monthly_description = models.TextField(
        blank=True,
        default="Pay month-to-month. Cancel anytime. Credits refresh each billing period.",
    )
    yearly_toggle_label = models.CharField(max_length=64, default="Yearly")
    yearly_description = models.TextField(
        blank=True,
        default="One payment per year — best value for studios with steady output.",
    )
    yearly_discount_note = models.CharField(
        max_length=120,
        blank=True,
        default="Save ~17% vs monthly",
    )
    credits_section_title = models.CharField(max_length=200, default="Buy credits")
    credits_section_description = models.TextField(
        blank=True,
        default="Top up anytime. Purchased credits never expire and stack with your plan allowance.",
    )
    credits_footer_note = models.TextField(
        blank=True,
        default="Credits are consumed per render based on the model selected in the editor.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pricing_settings"
        verbose_name = "pricing settings"
        verbose_name_plural = "pricing settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls) -> "PricingSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Pricing page settings"


class Plan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=64)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    monthly_description = models.TextField(
        blank=True,
        help_text="Shown on pricing when Monthly billing is selected",
    )
    yearly_description = models.TextField(
        blank=True,
        help_text="Shown on pricing when Yearly billing is selected",
    )
    currency = models.CharField(max_length=3, default="USD")
    credits_monthly = models.PositiveIntegerField(default=100)
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "plans"
        ordering = ["sort_order", "price_monthly"]

    def __str__(self):
        return self.name


class BillingCycle(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CANCELLED = "cancelled", "Cancelled"
    TRIALING = "trialing", "Trialing"


class UserSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
    )
    billing_cycle = models.CharField(
        max_length=20,
        choices=BillingCycle.choices,
        default=BillingCycle.MONTHLY,
    )
    started_at = models.DateTimeField(default=timezone.now)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_subscriptions"

    def __str__(self):
        return f"{self.user.email} — {self.plan.name}"


class CreditPack(models.Model):
    """One-time credit purchase (top-up), managed in admin."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=64)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    credits = models.PositiveIntegerField()
    bonus_credits = models.PositiveIntegerField(
        default=0,
        help_text="Extra credits included in this pack",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "credit_packs"
        ordering = ["sort_order", "price"]

    @property
    def total_credits(self) -> int:
        return self.credits + self.bonus_credits

    def __str__(self):
        return f"{self.name} ({self.total_credits} credits)"
