"""
Resolve API endpoints for each AI model.

Priority:
  1. DB: AIProvider (base_url, api_key via env var name, adapter)
  2. AIModel.config.endpoint_path
  3. AIModel.external_id / provider defaults
  4. Legacy PROVIDER_REGISTRY + settings (.env) fallback
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from apps.catalog.provider_config import (
    get_ai_provider,
    resolve_provider_api_key,
    resolve_provider_base_url,
)
from apps.catalog.provider_fallback import PROVIDER_REGISTRY

if TYPE_CHECKING:
    from apps.catalog.models import AIModel


@dataclass(frozen=True)
class ModelEndpoint:
    provider: str
    base_url: str
    path: str
    api_key: str
    submit_method: str = "POST"
    output_type: str = "image"
    extra: dict[str, Any] | None = None

    @property
    def submit_url(self) -> str:
        base = self.base_url.rstrip("/")
        path = self.path.lstrip("/")
        return f"{base}/{path}" if path else base


def resolve_model_endpoint(model: AIModel) -> ModelEndpoint:
    provider_slug = (model.provider or "stub").lower().strip()
    cfg = dict(model.config or {})
    provider_row = get_ai_provider(provider_slug)
    reg = PROVIDER_REGISTRY.get(provider_slug, {})

    base_url = resolve_provider_base_url(provider_row, provider_slug)
    api_key = resolve_provider_api_key(provider_row, provider_slug)

    path = str(cfg.get("endpoint_path") or "").strip()
    if not path:
        external = str(model.external_id or "").strip()
        if provider_row and provider_row.path_template and external:
            path = provider_row.path_template.format(external_id=external)
        elif provider_row and provider_row.use_external_id_as_path and external:
            path = external
        elif provider_row and provider_row.default_path:
            path = provider_row.default_path
        else:
            template = reg.get("path_template")
            if template and external:
                path = template.format(external_id=external)
            elif external and reg.get("path_from") == "config_or_external":
                path = external
            else:
                path = str(reg.get("default_path") or external or "")

    category_slug = model.category.slug if model.category_id else ""
    output_type = str(
        cfg.get("output_type")
        or ("video" if category_slug == "image-to-video" else "image")
    )

    return ModelEndpoint(
        provider=provider_slug,
        base_url=base_url,
        path=path,
        api_key=api_key,
        output_type=output_type,
        extra={
            "poll_interval_sec": float(cfg.get("poll_interval_sec", 2)),
            "timeout_sec": int(cfg.get("timeout_sec", 300)),
        },
    )
