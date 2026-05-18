from django.db.models import Prefetch
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AIModel, CapabilityCategory, CategoryPromptPreset
from .serializers import CapabilityCategorySerializer
from .user_preset_views import UserPromptPresetViewSet

__all__ = ["CatalogView", "UserPromptPresetViewSet"]


class CatalogView(APIView):
    """Nested catalog: categories → prompt presets + models."""

    permission_classes = [AllowAny]

    def get(self, request):
        active_category_presets = CategoryPromptPreset.objects.filter(
            is_active=True
        ).order_by("sort_order", "title")
        active_models = AIModel.objects.filter(is_active=True).order_by(
            "sort_order", "name"
        )
        categories = (
            CapabilityCategory.objects.filter(is_active=True)
            .prefetch_related(
                Prefetch("prompt_presets", queryset=active_category_presets),
                Prefetch("models", queryset=active_models),
            )
            .order_by("sort_order", "name")
        )
        return Response(CapabilityCategorySerializer(categories, many=True).data)
