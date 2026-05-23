from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import AIModel
from apps.rendering.pricing import RenderPricingParams, estimate_fal_usd, estimate_render_credits


def _parse_bool(value: str | None) -> bool:
    if not value:
        return False
    return value.strip().lower() in ("1", "true", "yes", "on")


class CreditEstimateView(APIView):
    """Estimate credits for a catalog model + editor settings (public)."""

    permission_classes = [AllowAny]

    def get(self, request):
        category_slug = (request.query_params.get("category_slug") or "").strip()
        model_slug = (request.query_params.get("model_slug") or "").strip()
        if not category_slug or not model_slug:
            return Response(
                {"error": "category_slug and model_slug are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        model = (
            AIModel.objects.filter(
                category__slug=category_slug,
                slug=model_slug,
                is_active=True,
                category__is_active=True,
            )
            .select_related("category")
            .first()
        )
        if not model:
            return Response(
                {"error": "Model not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        duration_raw = request.query_params.get("duration_seconds") or request.query_params.get(
            "video_duration"
        )
        duration_seconds: float | None = None
        if duration_raw:
            text = str(duration_raw).replace("s", "").strip()
            try:
                duration_seconds = float(text)
            except ValueError:
                duration_seconds = None

        upscale_raw = request.query_params.get("upscale_scale") or request.query_params.get(
            "scale"
        )
        upscale_factor: float | None = None
        if upscale_raw:
            try:
                upscale_factor = float(upscale_raw)
            except ValueError:
                upscale_factor = None

        params = RenderPricingParams(
            resolution=(request.query_params.get("resolution") or "").strip() or None,
            duration_seconds=duration_seconds,
            generate_audio=_parse_bool(request.query_params.get("generate_audio")),
            upscale_factor=upscale_factor,
        )

        fal_usd = estimate_fal_usd(model, params, category_slug=category_slug)
        credits = estimate_render_credits(
            model,
            category_slug=category_slug,
            render_params=params,
        )

        return Response(
            {
                "credits": credits,
                "fal_usd_estimate": round(fal_usd, 4) if fal_usd is not None else None,
                "category_slug": category_slug,
                "model_slug": model_slug,
            }
        )
