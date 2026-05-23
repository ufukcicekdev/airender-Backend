"""Load AIProvider from DB (with settings fallback)."""

from __future__ import annotations

from apps.catalog.models import AIProvider
from apps.catalog.provider_fallback import PROVIDER_REGISTRY, env_setting


def get_ai_provider(slug: str) -> AIProvider | None:
    key = (slug or "").lower().strip()
    if not key or key == "stub":
        return None
    try:
        return AIProvider.objects.get(slug=key, is_active=True)
    except AIProvider.DoesNotExist:
        return None


def resolve_provider_base_url(provider_row: AIProvider | None, provider_slug: str) -> str:
    if provider_row and provider_row.base_url:
        return provider_row.base_url.rstrip("/")
    reg = PROVIDER_REGISTRY.get(provider_slug, {})
    return env_setting(
        reg.get("base_url_setting", ""),
        reg.get("default_base_url", ""),
    ).rstrip("/")


def resolve_provider_api_key(provider_row: AIProvider | None, provider_slug: str) -> str:
    if provider_row:
        key = provider_row.resolve_api_key()
        if key:
            return key
    reg = PROVIDER_REGISTRY.get(provider_slug, {})
    return env_setting(reg.get("api_key_setting", ""), "")


def resolve_provider_adapter_kind(provider_row: AIProvider | None, provider_slug: str) -> str:
    if provider_row:
        return provider_row.adapter
    if provider_slug in ("fal", "comfy", "google"):
        return provider_slug
    if provider_slug in PROVIDER_REGISTRY:
        return "http"
    return "stub"
