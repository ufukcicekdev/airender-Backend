"""
Fal.ai list prices for endpoints used in our catalog.

Sources: https://fal.ai/models/<endpoint> (pricing section), May 2026.
Update when Fal changes rates; margin is applied in pricing.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

PricingMode = Literal[
    "per_image_resolution",
    "per_image_flat",
    "per_second",
    "per_megapixel",
    "gpt_image_edit",
]


@dataclass(frozen=True)
class FalEndpointPricing:
    mode: PricingMode
    # per_image_resolution / per_image_flat
    usd_by_resolution: dict[str, float] | None = None
    usd_flat: float | None = None
    # per_second (video)
    usd_per_second: float | None = None
    usd_per_second_with_audio: float | None = None
    # per_megapixel (flux, clarity)
    usd_per_megapixel: float | None = None
    default_megapixels: float = 1.0
    # gpt-image-1.5/edit default quality tiers (USD per image)
    gpt_usd_by_quality: dict[str, float] | None = None
    notes: str = ""


# Keys must match AIModel.config["endpoint_path"] (lowercase).
FAL_ENDPOINT_PRICING: dict[str, FalEndpointPricing] = {
    # --- Image edit / generate (Nano Banana family) ---
    "fal-ai/nano-banana/edit": FalEndpointPricing(
        mode="per_image_resolution",
        usd_by_resolution={"1k": 0.08, "2k": 0.12, "4k": 0.16, "default": 0.08},
        notes="Nano Banana 2 edit — fal.ai/learn/tools/nano-banana-pro-vs-nano-banana-2",
    ),
    "fal-ai/nano-banana": FalEndpointPricing(
        mode="per_image_resolution",
        usd_by_resolution={"1k": 0.08, "2k": 0.12, "4k": 0.16, "default": 0.08},
        notes="Nano Banana 2 text-to-image",
    ),
    "fal-ai/nano-banana-pro/edit": FalEndpointPricing(
        mode="per_image_resolution",
        usd_by_resolution={"1k": 0.15, "2k": 0.15, "4k": 0.30, "default": 0.15},
        notes="Nano Banana Pro edit",
    ),
    "fal-ai/nano-banana-pro": FalEndpointPricing(
        mode="per_image_resolution",
        usd_by_resolution={"1k": 0.15, "2k": 0.15, "4k": 0.30, "default": 0.15},
        notes="Nano Banana Pro text-to-image",
    ),
    # --- Flux ---
    "fal-ai/flux-pro": FalEndpointPricing(
        mode="per_megapixel",
        usd_per_megapixel=0.05,
        default_megapixels=1.0,
        notes="FLUX.1 [pro] — $0.05 / MP",
    ),
    # --- GPT Image ---
    "fal-ai/gpt-image-1.5": FalEndpointPricing(
        mode="gpt_image_edit",
        gpt_usd_by_quality={"low": 0.009, "medium": 0.034, "high": 0.133, "default": 0.133},
        notes="GPT Image 1.5 — high quality 1024 default",
    ),
    "fal-ai/gpt-image-1.5/edit": FalEndpointPricing(
        mode="gpt_image_edit",
        gpt_usd_by_quality={"low": 0.009, "medium": 0.034, "high": 0.133, "default": 0.133},
        notes="GPT Image 1.5 edit — high quality default",
    ),
    # --- Seedream ---
    "fal-ai/bytedance/seedream/v4/text-to-image": FalEndpointPricing(
        mode="per_image_flat",
        usd_flat=0.03,
        notes="Seedream V4 — $0.03 / image",
    ),
    "fal-ai/bytedance/seedream/v4/edit": FalEndpointPricing(
        mode="per_image_flat",
        usd_flat=0.03,
        notes="Seedream V4 edit (same tier as t2i on Fal)",
    ),
    # --- Upscale (Magnific via clarity on generate tab) ---
    "fal-ai/clarity-upscaler": FalEndpointPricing(
        mode="per_megapixel",
        usd_per_megapixel=0.03,
        default_megapixels=4.0,
        notes="Clarity upscaler — $0.03 / MP; default assumes ~2x upscale output",
    ),
    # --- Video ---
    "fal-ai/veo3/image-to-video": FalEndpointPricing(
        mode="per_second",
        usd_per_second=0.20,
        usd_per_second_with_audio=0.40,
        notes="Veo 3 image-to-video",
    ),
    "fal-ai/kling-video/v1.6/standard/image-to-video": FalEndpointPricing(
        mode="per_second",
        usd_per_second=0.056,
        usd_per_second_with_audio=0.056,
        notes="Kling 1.6 std — $0.056/s",
    ),
    # Legacy catalog paths (conservative estimates if endpoint still used)
    "fal-ai/bytedance/seedance/v1/image-to-video": FalEndpointPricing(
        mode="per_second",
        usd_per_second=0.12,
        usd_per_second_with_audio=0.12,
        notes="Seedance v1 — estimate; prefer seedance-2.0 endpoint when migrating",
    ),
    "fal-ai/runway-gen3/turbo/image-to-video": FalEndpointPricing(
        mode="per_second",
        usd_per_second=0.10,
        usd_per_second_with_audio=0.10,
        notes="Runway Gen-3 turbo — estimate; verify on fal.ai if endpoint changes",
    ),
}

# Output megapixels by UI resolution tier (approximate for billing).
RESOLUTION_TO_MP: dict[str, float] = {
    "1k": 1.0,
    "2k": 4.0,
    "4k": 16.0,
    "720p": 0.9,
    "1080p": 2.0,
}


def normalize_endpoint_path(path: str | None) -> str:
    return (path or "").strip().lower().rstrip("/")


def lookup_fal_pricing(endpoint_path: str | None) -> FalEndpointPricing | None:
    key = normalize_endpoint_path(endpoint_path)
    if not key:
        return None
    if key in FAL_ENDPOINT_PRICING:
        return FAL_ENDPOINT_PRICING[key]
    # Prefix match for minor path variants
    for registered, rule in FAL_ENDPOINT_PRICING.items():
        if key.startswith(registered) or registered.startswith(key):
            return rule
    return None


def fal_usd_for_endpoint(
    endpoint_path: str | None,
    *,
    resolution: str | None = None,
    duration_seconds: float | None = None,
    generate_audio: bool = False,
    upscale_factor: float | None = None,
    num_images: int = 1,
    model_config: dict[str, Any] | None = None,
) -> float | None:
    """Return estimated Fal USD cost before margin, or None if unknown."""
    rule = lookup_fal_pricing(endpoint_path)
    if rule is None:
        cfg = model_config or {}
        pricing = cfg.get("pricing") if isinstance(cfg.get("pricing"), dict) else None
        if pricing and "fal_usd_flat" in pricing:
            return float(pricing["fal_usd_flat"]) * max(1, num_images)
        return None

    res_key = (resolution or "default").strip().lower()
    if res_key.endswith("k") and res_key[:-1].isdigit():
        res_key = res_key  # 1k, 2k, 4k

    if rule.mode == "per_image_resolution":
        table = rule.usd_by_resolution or {}
        unit = table.get(res_key) or table.get("default", 0.08)
        return float(unit) * max(1, num_images)

    if rule.mode == "per_image_flat":
        return float(rule.usd_flat or 0.03) * max(1, num_images)

    if rule.mode == "per_megapixel":
        mp = RESOLUTION_TO_MP.get(res_key, rule.default_megapixels)
        factor = float(upscale_factor or 1.0)
        if factor > 1:
            mp *= factor * factor
        return float(rule.usd_per_megapixel or 0.05) * mp * max(1, num_images)

    if rule.mode == "gpt_image_edit":
        table = rule.gpt_usd_by_quality or {}
        quality = (model_config or {}).get("default_quality", "high")
        unit = table.get(str(quality).lower()) or table.get("default", 0.133)
        return float(unit) * max(1, num_images)

    if rule.mode == "per_second":
        seconds = max(1.0, float(duration_seconds or 4))
        rate = float(rule.usd_per_second or 0.1)
        if generate_audio and rule.usd_per_second_with_audio:
            rate = float(rule.usd_per_second_with_audio)
        return rate * seconds

    return None
