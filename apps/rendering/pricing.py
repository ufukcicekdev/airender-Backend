"""Convert Fal USD estimates + margin into site credits."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from django.conf import settings

from apps.catalog.models import AIModel

from .fal_pricing import fal_usd_for_endpoint, normalize_endpoint_path


@dataclass
class RenderPricingParams:
    resolution: str | None = None
    duration_seconds: float | None = None
    generate_audio: bool = False
    upscale_factor: float | None = None
    num_images: int = 1

    @classmethod
    def from_node_data(
        cls, data: dict[str, Any], category_slug: str
    ) -> RenderPricingParams:
        resolution = data.get("resolution")
        if isinstance(resolution, str):
            resolution = resolution.strip().lower()
        else:
            resolution = None

        duration_seconds: float | None = None
        if category_slug == "image-to-video":
            raw = data.get("video_duration") or data.get("duration") or "4"
            if isinstance(raw, str):
                raw = raw.replace("s", "").strip()
            try:
                duration_seconds = float(raw)
            except (TypeError, ValueError):
                duration_seconds = 4.0

        generate_audio = bool(data.get("generate_audio", False))

        upscale_factor: float | None = None
        if category_slug == "upscale":
            scale = data.get("upscale_scale") or data.get("scale")
            try:
                upscale_factor = float(scale) if scale is not None else 2.0
            except (TypeError, ValueError):
                upscale_factor = 2.0

        return cls(
            resolution=resolution,
            duration_seconds=duration_seconds,
            generate_audio=generate_audio,
            upscale_factor=upscale_factor,
            num_images=1,
        )

    @classmethod
    def defaults_for_category(cls, category_slug: str) -> RenderPricingParams:
        if category_slug == "image-to-video":
            return cls(
                resolution="720p",
                duration_seconds=4.0,
                generate_audio=False,
            )
        if category_slug == "image-edit":
            return cls(resolution="1k")
        if category_slug == "upscale":
            return cls(upscale_factor=2.0)
        return cls(resolution="1k")


def credit_economics() -> dict[str, float]:
    raw = getattr(settings, "CREDIT_ECONOMICS", None) or {}
    return {
        "usd_per_credit": float(raw.get("USD_PER_CREDIT", 0.015)),
        "margin_percent": float(raw.get("RENDER_MARGIN_PERCENT", 40)),
        "min_credits": float(raw.get("MIN_CREDITS", 1)),
    }


def usd_to_credits(fal_usd: float) -> int:
    econ = credit_economics()
    usd_per_credit = max(econ["usd_per_credit"], 0.001)
    margin = max(econ["margin_percent"], 0) / 100.0
    charge_usd = fal_usd * (1.0 + margin)
    credits = math.ceil(charge_usd / usd_per_credit)
    return max(int(econ["min_credits"]), credits)


def estimate_fal_usd(
    model: AIModel,
    params: RenderPricingParams | None,
    *,
    category_slug: str,
) -> float | None:
    cfg = dict(model.config or {})
    endpoint = normalize_endpoint_path(cfg.get("endpoint_path") or model.external_id)
    p = params or RenderPricingParams.defaults_for_category(category_slug)

    if model.provider != "fal":
        return None

    return fal_usd_for_endpoint(
        endpoint,
        resolution=p.resolution,
        duration_seconds=p.duration_seconds,
        generate_audio=p.generate_audio,
        upscale_factor=p.upscale_factor,
        num_images=p.num_images,
        model_config=cfg,
    )


def estimate_render_credits(
    model: AIModel | None,
    *,
    category_slug: str,
    render_params: RenderPricingParams | None = None,
    node_data: dict[str, Any] | None = None,
) -> int:
    if model is None:
        return 1

    params = render_params
    if params is None and node_data is not None:
        params = RenderPricingParams.from_node_data(node_data, category_slug)
    if params is None:
        params = RenderPricingParams.defaults_for_category(category_slug)

    fal_usd = estimate_fal_usd(model, params, category_slug=category_slug)
    if fal_usd is not None and fal_usd > 0:
        return usd_to_credits(fal_usd)

    # Non-Fal providers: legacy flat credit_cost from catalog
    return max(1, int(model.credit_cost or 1))


def estimate_render_credits_from_graph(
    graph: dict[str, Any],
    render_node_id: str | None,
    model: AIModel | None,
    category_slug: str,
) -> int:
    from .render_context import get_render_node

    node, _ = get_render_node(graph, render_node_id)
    node_data = (node.get("data") or {}) if node else {}
    return estimate_render_credits(
        model,
        category_slug=category_slug,
        node_data=node_data,
    )
