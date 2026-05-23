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
    "google": {
        "base_url_setting": "GOOGLE_AI_API_BASE",
        "default_base_url": "https://generativelanguage.googleapis.com/v1beta",
        "api_key_setting": "GOOGLE_AI_API_KEY",
        "path_from": "config_or_external",
    },
    "kling": {
        "base_url_setting": "KLING_API_BASE",
        "default_base_url": "https://api.klingai.com/v1",
        "api_key_setting": "KLING_API_KEY",
        "default_path": "",
    },
    "runway": {
        "base_url_setting": "RUNWAY_API_BASE",
        "default_base_url": "https://api.runwayml.com/v1",
        "api_key_setting": "RUNWAY_API_KEY",
        "default_path": "",
    },
    "bytedance": {
        "base_url_setting": "BYTEDANCE_API_BASE",
        "default_base_url": "https://api.byteplus.com/v1",
        "api_key_setting": "BYTEDANCE_API_KEY",
        "default_path": "",
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
