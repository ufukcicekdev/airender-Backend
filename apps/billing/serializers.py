from rest_framework import serializers

from .models import BillingCycle, CreditPack, Plan, PricingSettings, UserSubscription


class PricingSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingSettings
        fields = (
            "plans_section_title",
            "plans_section_description",
            "monthly_toggle_label",
            "monthly_description",
            "yearly_toggle_label",
            "yearly_description",
            "yearly_discount_note",
            "credits_section_title",
            "credits_section_description",
            "credits_footer_note",
        )


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            "id",
            "slug",
            "name",
            "description",
            "price_monthly",
            "price_yearly",
            "monthly_description",
            "yearly_description",
            "currency",
            "credits_monthly",
            "features",
            "is_popular",
        )


class CreditPackSerializer(serializers.ModelSerializer):
    total_credits = serializers.IntegerField(read_only=True)

    class Meta:
        model = CreditPack
        fields = (
            "id",
            "slug",
            "name",
            "description",
            "credits",
            "bonus_credits",
            "total_credits",
            "price",
            "currency",
            "features",
            "is_popular",
        )


class PricingOverviewSerializer(serializers.Serializer):
    settings = PricingSettingsSerializer()
    plans = PlanSerializer(many=True)
    credit_packs = CreditPackSerializer(many=True)


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = (
            "id",
            "plan",
            "status",
            "billing_cycle",
            "started_at",
            "current_period_end",
        )


class SubscribeSerializer(serializers.Serializer):
    plan_slug = serializers.SlugField()
    billing_cycle = serializers.ChoiceField(
        choices=BillingCycle.choices,
        default=BillingCycle.MONTHLY,
    )


class PurchaseCreditsSerializer(serializers.Serializer):
    pack_slug = serializers.SlugField()
