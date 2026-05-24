from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalog.category_presets import CATEGORY_PRESETS
from apps.catalog.image_edit_models import IMAGE_EDIT_ACTIVE_SLUGS, IMAGE_EDIT_MODELS
from apps.catalog.image_generate_models import (
    IMAGE_GENERATE_ACTIVE_SLUGS,
    IMAGE_GENERATE_MODELS,
)
from apps.catalog.upscale_models import UPSCALE_ACTIVE_SLUGS, UPSCALE_MODELS
from apps.catalog.video_models import VIDEO_ACTIVE_SLUGS, VIDEO_MODELS
from apps.catalog.model_3d_models import MODEL_3D_ACTIVE_SLUGS, MODEL_3D_MODELS
from apps.catalog.models import (
    AIModel,
    AIProvider,
    CapabilityCategory,
    CategoryPromptPreset,
    ModelPromptPreset,
)


class Command(BaseCommand):
    help = "Seed capability categories, AI models, and prompt presets"

    def handle(self, *args, **options):
        catalog = [
            {
                "slug": "image-generate",
                "name": "Image Generate",
                "description": "Text or sketch to photorealistic image",
                "icon": "image",
                "sort_order": 0,
                "models": IMAGE_GENERATE_MODELS,
            },
            {
                "slug": "image-to-video",
                "name": "Video Creator",
                "description": "Animate still frames into short clips",
                "icon": "video",
                "sort_order": 1,
                "models": VIDEO_MODELS,
            },
            {
                "slug": "image-edit",
                "name": "Image Editor",
                "description": "Inpaint, relight, and restyle existing images",
                "icon": "wand-sparkles",
                "sort_order": 2,
                "models": IMAGE_EDIT_MODELS,
            },
            {
                "slug": "3d-model",
                "name": "3D Model Create",
                "description": "Text or image to 3D mesh — export GLB/OBJ",
                "icon": "box",
                "sort_order": 3,
                "models": MODEL_3D_MODELS,
            },
            {
                "slug": "upscale",
                "name": "Image Upscaler",
                "description": "Increase resolution and detail",
                "icon": "maximize-2",
                "sort_order": 4,
                "models": UPSCALE_MODELS,
            },
        ]

        for cat_data in catalog:
            models_data = cat_data.pop("models")
            category, _ = CapabilityCategory.objects.update_or_create(
                slug=cat_data["slug"],
                defaults={**cat_data, "is_active": True},
            )

            category_presets_data = CATEGORY_PRESETS.get(category.slug, [])
            category_active_slugs: list[str] = []
            for i, preset in enumerate(category_presets_data):
                slug = slugify(preset["title"])[:64]
                category_active_slugs.append(slug)
                CategoryPromptPreset.objects.update_or_create(
                    category=category,
                    slug=slug,
                    defaults={
                        "title": preset["title"],
                        "icon": preset.get("icon", ""),
                        "positive_prompt": preset["positive"],
                        "negative_prompt": preset.get("negative", ""),
                        "is_default": preset.get("is_default", False),
                        "is_active": True,
                        "sort_order": i,
                    },
                )
            if category_active_slugs:
                CategoryPromptPreset.objects.filter(category=category).exclude(
                    slug__in=category_active_slugs
                ).update(is_active=False)
                ModelPromptPreset.objects.filter(model__category=category).update(
                    is_active=False
                )

            for model_data in models_data:
                presets_data = model_data.pop("presets", [])
                if category.slug == "3d-model":
                    cfg = dict(model_data.get("config") or {})
                    cfg.setdefault("output_type", "model3d")
                    model_data["config"] = cfg
                model, _ = AIModel.objects.update_or_create(
                    category=category,
                    slug=model_data["slug"],
                    defaults={**model_data, "is_active": True},
                )
                active_slugs: list[str] = []
                for i, preset in enumerate(presets_data):
                    slug = slugify(preset["title"])[:64]
                    active_slugs.append(slug)
                    ModelPromptPreset.objects.update_or_create(
                        model=model,
                        slug=slug,
                        defaults={
                            "title": preset["title"],
                            "icon": preset.get("icon", ""),
                            "positive_prompt": preset["positive"],
                            "negative_prompt": preset.get("negative", ""),
                            "is_default": preset.get("is_default", False),
                            "is_active": True,
                            "sort_order": i,
                        },
                    )
                if active_slugs:
                    ModelPromptPreset.objects.filter(model=model).exclude(
                        slug__in=active_slugs
                    ).update(is_active=False)

        # Legacy: Meshy moved from image-edit → 3d-model
        AIModel.objects.filter(
            category__slug="image-edit", slug="meshy"
        ).update(is_active=False)
        AIModel.objects.filter(category__slug="image-edit").exclude(
            slug__in=IMAGE_EDIT_ACTIVE_SLUGS
        ).update(is_active=False)
        AIModel.objects.filter(category__slug="upscale").exclude(
            slug__in=UPSCALE_ACTIVE_SLUGS
        ).update(is_active=False)
        AIModel.objects.filter(category__slug="image-to-video").exclude(
            slug__in=VIDEO_ACTIVE_SLUGS
        ).update(is_active=False)
        AIModel.objects.filter(category__slug="image-generate").exclude(
            slug__in=IMAGE_GENERATE_ACTIVE_SLUGS
        ).update(is_active=False)
        AIModel.objects.filter(category__slug="3d-model").exclude(
            slug__in=MODEL_3D_ACTIVE_SLUGS
        ).update(is_active=False)

        AIProvider.objects.filter(slug="fal").update(
            is_active=True,
            use_external_id_as_path=True,
        )
        AIProvider.objects.filter(slug="google").update(is_active=False)

        self.stdout.write(
            self.style.SUCCESS(
                f"Catalog seeded: {CapabilityCategory.objects.count()} categories, "
                f"{AIModel.objects.filter(is_active=True).count()} active models, "
                f"{CategoryPromptPreset.objects.filter(is_active=True).count()} category presets."
            )
        )
