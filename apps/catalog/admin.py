from django import forms
from django.contrib import admin

from .models import (
    AIModel,
    AIProvider,
    CapabilityCategory,
    CategoryPromptPreset,
    ModelPromptPreset,
    UserPromptPreset,
)


class CategoryPromptPresetInline(admin.TabularInline):
    model = CategoryPromptPreset
    extra = 1
    fields = (
        "title",
        "slug",
        "icon",
        "positive_prompt",
        "negative_prompt",
        "is_default",
        "is_active",
        "sort_order",
    )
    prepopulated_fields = {"slug": ("title",)}


class ModelPromptPresetInline(admin.TabularInline):
    model = ModelPromptPreset
    extra = 1
    fields = (
        "title",
        "slug",
        "icon",
        "positive_prompt",
        "negative_prompt",
        "is_default",
        "is_active",
        "sort_order",
    )
    prepopulated_fields = {"slug": ("title",)}


class AIModelInline(admin.TabularInline):
    model = AIModel
    extra = 0
    fields = (
        "name",
        "slug",
        "tag",
        "brand_icon",
        "provider",
        "credit_cost",
        "is_active",
        "sort_order",
    )
    prepopulated_fields = {"slug": ("name",)}
    show_change_link = True


@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    list_editable = ("is_active", "sort_order")
    list_display = (
        "name",
        "slug",
        "adapter",
        "base_url",
        "api_key_env_var",
        "is_active",
        "sort_order",
    )
    list_filter = ("is_active", "adapter")
    search_fields = ("name", "slug", "api_key_env_var")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order",)
    fieldsets = (
        (
            None,
            {
                "fields": ("name", "slug", "adapter", "is_active", "sort_order"),
            },
        ),
        (
            "Connection",
            {
                "fields": (
                    "base_url",
                    "api_key_env_var",
                    "default_path",
                    "path_template",
                    "use_external_id_as_path",
                ),
                "description": (
                    "Token/secret DB'de tutulmaz. Railway'de api_key_env_var adıyla "
                    "env ekleyin (ör. MIDJOURNEY_API_KEY). Deploy gerekmez — sadece "
                    "container restart / env güncellemesi."
                ),
            },
        ),
    )


@admin.register(CapabilityCategory)
class CapabilityCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order",)
    inlines = [CategoryPromptPresetInline, AIModelInline]


class AIModelAdminForm(forms.ModelForm):
    class Meta:
        model = AIModel
        fields = "__all__"
        widgets = {
            "config": forms.Textarea(
                attrs={
                    "rows": 10,
                    "cols": 80,
                    "style": "font-family: ui-monospace, monospace; font-size: 13px;",
                    "placeholder": (
                        '{\n  "endpoint_path": "fal-ai/flux-pro",\n'
                        '  "output_type": "image"\n}'
                    ),
                }
            ),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    form = AIModelAdminForm
    list_display = (
        "name",
        "category",
        "slug",
        "tag",
        "brand_icon",
        "provider",
        "credit_cost",
        "is_active",
        "sort_order",
    )
    list_filter = ("is_active", "category", "provider", "tag")
    list_editable = ("is_active", "sort_order", "credit_cost")
    search_fields = ("name", "slug", "external_id", "provider")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("category", "sort_order")
    inlines = [ModelPromptPresetInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "category",
                    "name",
                    "slug",
                    "description",
                    "tag",
                    "brand_icon",
                    "is_active",
                    "sort_order",
                )
            },
        ),
        (
            "Provider",
            {
                "fields": ("provider", "external_id", "credit_cost", "config"),
                "description": (
                    "provider = AI Providers → slug. "
                    "config: endpoint_path, output_type (image|video), poll_interval_sec. "
                    "Yeni servis: Admin → AI Providers + Railway env (deploy yok)."
                ),
            },
        ),
        (
            "Editor inputs (Vizmaker-style)",
            {
                "fields": (
                    "requires_images",
                    "min_input_images",
                    "max_input_images",
                    "input_images_label",
                    "input_images_help",
                ),
            },
        ),
        (
            "Defaults",
            {"fields": ("default_positive", "default_negative")},
        ),
    )


@admin.register(CategoryPromptPreset)
class CategoryPromptPresetAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_default", "is_active", "sort_order")
    list_filter = ("is_active", "is_default", "category")
    search_fields = ("title", "positive_prompt", "category__name")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("category",)


@admin.register(UserPromptPreset)
class UserPromptPresetAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "sort_order", "updated_at")
    list_filter = ("category",)
    search_fields = ("title", "positive_prompt", "user__email")
    raw_id_fields = ("user", "category")


@admin.register(ModelPromptPreset)
class ModelPromptPresetAdmin(admin.ModelAdmin):
    list_display = ("title", "model", "is_default", "is_active", "sort_order")
    list_filter = ("is_active", "is_default", "model__category")
    search_fields = ("title", "positive_prompt", "model__name")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("model",)
