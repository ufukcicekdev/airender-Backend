"""Legacy .env fallback when AIProvider DB row is missing."""

from __future__ import annotations

from typing import Any

from django.conf import settings

PROVIDER_REGISTRY: dict[str, dict[str, Any]] = {
    "fal": {
        "base_url_setting": "FAL_API_BASE",
        "default_base_url": "https://queue.fal.run",
        "api_key_setting": "FAL_API_KEY",
        "path_from": "config_or_external",
    },
    "replicate": {
        "base_url_setting": "REPLICATE_API_BASE",
        "default_base_url": "https://api.replicate.com/v1",
        "api_key_setting": "REPLICATE_API_TOKEN",
        "path_template": "models/{external_id}/predictions",
    },
    "openai": {
        "base_url_setting": "OPENAI_API_BASE",
        "default_base_url": "https://api.openai.com/v1",
        "api_key_setting": "OPENAI_API_KEY",
        "default_path": "images/edits",
    },
    "magnific": {
        "base_url_setting": "MAGNIFIC_API_BASE",
        "default_base_url": "https://api.magnific.ai/v1",
        "api_key_setting": "MAGNIFIC_API_KEY",
        "default_path": "upscale",
    },
    "comfy": {
        "base_url_setting": "COMFYUI_URL",
        "default_base_url": "",
        "api_key_setting": "",
        "default_path": "prompt",
    },
}


def env_setting(name: str, default: str = "") -> str:
    return str(getattr(settings, name, default) or default)
