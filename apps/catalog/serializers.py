from rest_framework import serializers

from .models import (
    AIModel,
    CapabilityCategory,
    CategoryPromptPreset,
    ModelPromptPreset,
    UserPromptPreset,
)


class PromptPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryPromptPreset
        fields = (
            "id",
            "slug",
            "title",
            "icon",
            "positive_prompt",
            "negative_prompt",
            "is_default",
        )


class ModelPromptPresetSerializer(PromptPresetSerializer):
    class Meta(PromptPresetSerializer.Meta):
        model = ModelPromptPreset


class CategoryPromptPresetSerializer(PromptPresetSerializer):
    class Meta(PromptPresetSerializer.Meta):
        model = CategoryPromptPreset


class AIModelSerializer(serializers.ModelSerializer):
    credit_cost = serializers.SerializerMethodField()
    credit_cost_from = serializers.SerializerMethodField()

    class Meta:
        model = AIModel
        fields = (
            "id",
            "slug",
            "name",
            "description",
            "tag",
            "brand_icon",
            "provider",
            "external_id",
            "credit_cost",
            "credit_cost_from",
            "requires_images",
            "min_input_images",
            "max_input_images",
            "input_images_label",
            "input_images_help",
            "config",
            "default_positive",
            "default_negative",
        )

    def _category_slug(self, obj: AIModel) -> str:
        cat = getattr(obj, "category", None)
        return cat.slug if cat else ""

    def get_credit_cost(self, obj: AIModel) -> int:
        from apps.rendering.pricing import RenderPricingParams, estimate_render_credits

        slug = self._category_slug(obj)
        return estimate_render_credits(
            obj,
            category_slug=slug,
            render_params=RenderPricingParams.defaults_for_category(slug),
        )

    def get_credit_cost_from(self, obj: AIModel) -> int:
        return self.get_credit_cost(obj)


class UserPromptPresetSerializer(serializers.ModelSerializer):
    category_slug = serializers.SlugField(write_only=True, required=False)
    category_slug_display = serializers.CharField(source="category.slug", read_only=True)

    class Meta:
        model = UserPromptPreset
        fields = (
            "id",
            "title",
            "icon",
            "positive_prompt",
            "negative_prompt",
            "category_slug",
            "category_slug_display",
            "sort_order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "category_slug_display")

    def _resolve_category(self, slug: str) -> CapabilityCategory:
        try:
            return CapabilityCategory.objects.get(slug=slug, is_active=True)
        except CapabilityCategory.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"category_slug": "Unknown capability category."}
            ) from exc

    def create(self, validated_data):
        slug = validated_data.pop("category_slug", None) or self.initial_data.get(
            "category_slug"
        )
        if not slug:
            raise serializers.ValidationError(
                {"category_slug": "This field is required."}
            )
        category = self._resolve_category(slug)
        user = self.context["request"].user
        return UserPromptPreset.objects.create(
            user=user, category=category, **validated_data
        )

    def update(self, instance, validated_data):
        slug = validated_data.pop("category_slug", None)
        if slug:
            instance.category = self._resolve_category(slug)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CapabilityCategorySerializer(serializers.ModelSerializer):
    models = AIModelSerializer(many=True, read_only=True)
    prompt_presets = CategoryPromptPresetSerializer(many=True, read_only=True)

    class Meta:
        model = CapabilityCategory
        fields = (
            "id",
            "slug",
            "name",
            "description",
            "icon",
            "prompt_presets",
            "models",
        )
