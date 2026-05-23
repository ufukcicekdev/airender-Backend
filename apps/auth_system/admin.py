from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import SignupSettings, User


@admin.register(SignupSettings)
class SignupSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "New user registration",
            {
                "fields": ("free_signup_credits",),
                "description": (
                    "Every new account created via registration receives this many credits. "
                    "Changing this value does not affect existing users."
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return not SignupSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "is_verified", "credits", "created_at")
    list_editable = ("credits",)
    search_fields = ("email", "username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Credits",
            {
                "fields": ("credits",),
                "description": (
                    "Invite-only billing: set the user's credit balance here after manual payment."
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2", "credits"),
            },
        ),
    )

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("credits", SignupSettings.load().free_signup_credits)
        return initial
