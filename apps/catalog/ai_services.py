"""
AI servisleri → backend/.env eşlemesi.

Ana render akışı: Fal.ai queue API (AIModel.provider = fal, config.endpoint_path = fal-ai/...).
Comfy / Magnific / 3D sağlayıcıları doğrudan API ile kalabilir.
"""

from __future__ import annotations

AI_SERVICE_ENV: dict[str, dict[str, str | list[str]]] = {
    "fal": {
        "label": "Fal.ai (primary — image, edit, video)",
        "env": ["FAL_API_KEY"],
        "optional_env": ["FAL_API_BASE"],
        "used_by": [
            "image-edit/*",
            "image-generate/nano-banana*",
            "image-generate/flux-pro",
            "image-generate/gpt-image",
            "image-generate/seedream",
            "image-generate/magnific",
            "image-to-video/*",
        ],
    },
    "replicate": {
        "label": "Replicate (optional direct)",
        "env": ["REPLICATE_API_TOKEN"],
        "optional_env": ["REPLICATE_API_BASE"],
        "used_by": [],
    },
    "openai": {
        "label": "OpenAI Images (optional direct)",
        "env": ["OPENAI_API_KEY"],
        "optional_env": ["OPENAI_API_BASE"],
        "used_by": [],
    },
    "magnific": {
        "label": "Magnific (upscale)",
        "env": ["MAGNIFIC_API_KEY"],
        "optional_env": ["MAGNIFIC_API_BASE"],
        "used_by": ["upscale/magnific-*"],
    },
    "comfy": {
        "label": "ComfyUI (optional self-hosted)",
        "env": ["COMFYUI_URL"],
        "used_by": [
            "upscale/pro-upscaler",
            "image-generate/flux-schnell",
            "image-generate/sdxl-arch",
        ],
    },
    "meshy": {
        "label": "Meshy 3D",
        "env": ["MESHY_API_KEY"],
        "used_by": ["3d-model/meshy-*"],
    },
    "tripo": {
        "label": "Tripo 3D",
        "env": ["TRIPO_API_KEY"],
        "used_by": ["3d-model/tripo-*"],
    },
    "hyperhuman": {
        "label": "Hyperhuman",
        "env": ["HYPERHUMAN_API_KEY"],
        "used_by": ["3d-model/hyperhuman-3d"],
    },
    "tencent": {
        "label": "Tencent Hunyuan 3D",
        "env": ["TENCENT_AI_API_KEY"],
        "used_by": ["3d-model/hunyuan-3d"],
    },
    "luma": {
        "label": "Luma AI",
        "env": ["LUMA_API_KEY"],
        "used_by": ["3d-model/luma-3d"],
    },
    "csm": {
        "label": "CSM",
        "env": ["CSM_API_KEY"],
        "used_by": ["3d-model/csm-ai"],
    },
}

ACTIVE_EDITOR_CATEGORIES = (
    "image-generate",
    "image-to-video",
    "image-edit",
    "upscale",
)

REQUIRED_ENV_FOR_EDITOR = [
    "FAL_API_KEY",
]
