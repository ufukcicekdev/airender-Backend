"""Provider router — Fal-style single entry, multiple backends."""

from __future__ import annotations

import logging

from apps.catalog.models import AIModel
from apps.catalog.provider_config import get_ai_provider, resolve_provider_adapter_kind

from .base import ProgressCallback, ProviderAdapter
from .comfy import ComfyAdapter
from .external import ExternalHttpAdapter
from .fal import FalAdapter
from .job import RenderJob
from .stub import StubAdapter

logger = logging.getLogger(__name__)

_ADAPTERS: dict[str, ProviderAdapter] = {
    "comfy": ComfyAdapter(),
    "fal": FalAdapter(),
    "replicate": ExternalHttpAdapter("replicate"),
    "openai": ExternalHttpAdapter("openai"),
    "magnific": ExternalHttpAdapter("magnific"),
    "runway": ExternalHttpAdapter("runway"),
    "google": ExternalHttpAdapter("google"),
    "kling": ExternalHttpAdapter("kling"),
    "bytedance": ExternalHttpAdapter("bytedance"),
    "meshy": ExternalHttpAdapter("meshy"),
    "tripo": ExternalHttpAdapter("tripo"),
    "hyperhuman": ExternalHttpAdapter("hyperhuman"),
    "tencent": ExternalHttpAdapter("tencent"),
    "luma": ExternalHttpAdapter("luma"),
    "csm": ExternalHttpAdapter("csm"),
    "stub": StubAdapter(),
}


def get_adapter(provider_key: str) -> ProviderAdapter:
    key = (provider_key or "stub").lower().strip()
    if key == "stub":
        return _ADAPTERS["stub"]

    provider_row = get_ai_provider(key)
    adapter_kind = resolve_provider_adapter_kind(provider_row, key)

    if adapter_kind == "fal":
        return _ADAPTERS["fal"]
    if adapter_kind == "comfy":
        return _ADAPTERS["comfy"]
    if adapter_kind == "http":
        return ExternalHttpAdapter(key)

    adapter = _ADAPTERS.get(adapter_kind) or _ADAPTERS.get(key)
    if adapter is None:
        logger.warning("Unknown provider %r — using stub", provider_key)
        return _ADAPTERS["stub"]
    return adapter


def run_provider(
    model: AIModel,
    job: RenderJob,
    *,
    on_progress: ProgressCallback | None = None,
) -> str:
    """Route job to the adapter for model.provider."""
    adapter = get_adapter(model.provider)
    logger.info(
        "Provider run provider=%s model=%s category=%s",
        model.provider,
        model.slug,
        model.category.slug,
    )
    return adapter.run(model, job, on_progress=on_progress)


def resolve_ai_model(category_slug: str, model_slug: str) -> AIModel | None:
    if not category_slug or not model_slug:
        return None
    try:
        return AIModel.objects.select_related("category").get(
            category__slug=category_slug,
            slug=model_slug,
            is_active=True,
        )
    except AIModel.DoesNotExist:
        return None
