from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import UserPromptPreset
from .serializers import UserPromptPresetSerializer


class UserPromptPresetViewSet(viewsets.ModelViewSet):
    """CRUD for user-owned prompt presets, filtered by capability category."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserPromptPresetSerializer
    http_method_names = ["get", "post", "patch", "put", "delete", "head", "options"]

    def get_queryset(self):
        qs = UserPromptPreset.objects.filter(user=self.request.user).select_related(
            "category"
        )
        category_slug = self.request.query_params.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs.order_by("sort_order", "-created_at")
