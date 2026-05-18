"""
AI servisleri → backend/.env eşlemesi.

Kullanıcı sadece token/URL girer; iç router (Celery + ProviderRouter) doğru adapter'ı seçer.
Frontend hiçbir servise direkt bağlanmaz.
"""

from __future__ import annotations

# provider key (AIModel.provider) → env değişkenleri
AI_SERVICE_ENV: dict[str, dict[str, str | list[str]]] = {
    "comfy": {
        "label": "ComfyUI (self-hosted)",
        "env": ["COMFYUI_URL"],
        "used_by": ["upscale/pro-upscaler", "image-generate/flux-schnell", "image-generate/sdxl-arch"],
    },
    "fal": {
        "label": "Fal Queue API",
        "env": ["FAL_API_KEY"],
        "optional_env": ["FAL_API_BASE"],
        "used_by": [
            "image-edit/nano-banana*",
            "image-to-video/*",
            "image-generate/nano-banana*",
        ],
    },
    "replicate": {
        "label": "Replicate",
        "env": ["REPLICATE_API_TOKEN"],
        "optional_env": ["REPLICATE_API_BASE"],
        "used_by": ["image-edit/flux-pro", "image-generate/flux-pro"],
    },
    "openai": {
        "label": "OpenAI Images",
        "env": ["OPENAI_API_KEY"],
        "optional_env": ["OPENAI_API_BASE"],
        "used_by": ["image-edit/gpt-image*", "image-generate/gpt-image"],
    },
    "magnific": {
        "label": "Magnific",
        "env": ["MAGNIFIC_API_KEY"],
        "optional_env": ["MAGNIFIC_API_BASE"],
        "used_by": ["upscale/magnific-*", "image-generate/magnific"],
    },
    "bytedance": {
        "label": "ByteDance / Seedream",
        "env": ["BYTEDANCE_API_KEY"],
        "optional_env": ["BYTEDANCE_API_BASE"],
        "used_by": ["image-edit/seedream", "image-generate/seedream"],
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

# Editörde aktif kategoriler (frontend Make)
ACTIVE_EDITOR_CATEGORIES = (
    "image-generate",
    "image-to-video",
    "image-edit",
    "upscale",
)

# Bu kategoriler için minimum .env (çoğu model Fal üzerinden)
REQUIRED_ENV_FOR_EDITOR = [
    "COMFYUI_URL",
    "FAL_API_KEY",
    "REPLICATE_API_TOKEN",
    "OPENAI_API_KEY",
    "MAGNIFIC_API_KEY",
    "BYTEDANCE_API_KEY",
]
