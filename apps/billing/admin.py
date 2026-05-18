from django.contrib import admin

from .models import CreditPack, Plan, PricingSettings, UserSubscription


@admin.register(PricingSettings)
class PricingSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Subscription plans section",
            {
                "fields": ("plans_section_title", "plans_section_description"),
            },
        ),
        (
            "Monthly billing",
            {
                "fields": ("monthly_toggle_label", "monthly_description"),
            },
        ),
        (
            "Yearly billing",
            {
                "fields": (
                    "yearly_toggle_label",
                    "yearly_description",
                    "yearly_discount_note",
                ),
            },
        ),
        (
            "Credit packs section",
            {
                "fields": (
                    "credits_section_title",
                    "credits_section_description",
                    "credits_footer_note",
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return not PricingSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "price_monthly",
        "price_yearly",
        "credits_monthly",
        "is_active",
        "is_popular",
        "sort_order",
    )
    list_filter = ("is_active", "is_popular")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order",)
    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "is_active", "is_popular", "sort_order")}),
        (
            "Pricing",
            {
                "fields": (
                    "price_monthly",
                    "monthly_description",
                    "price_yearly",
                    "yearly_description",
                    "currency",
                    "credits_monthly",
                ),
            },
        ),
        ("Features", {"fields": ("features",)}),
    )


@admin.register(CreditPack)
class CreditPackAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "credits",
        "bonus_credits",
        "price",
        "is_active",
        "is_popular",
        "sort_order",
    )
    list_filter = ("is_active", "is_popular")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order",)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "billing_cycle", "started_at", "current_period_end")
    list_filter = ("status", "billing_cycle", "plan")
    search_fields = ("user__email", "user__username")
    raw_id_fields = ("user", "plan")
