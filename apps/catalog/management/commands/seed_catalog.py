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
from apps.catalog.models import AIModel, CapabilityCategory, CategoryPromptPreset, ModelPromptPreset


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
                "models": [
                    {
                        "slug": "meshy-3d",
                        "name": "Meshy AI",
                        "description": "Text or image to textured 3D model",
                        "tag": "pro",
                        "brand_icon": "meshy",
                        "provider": "meshy",
                        "external_id": "meshy-3d-v2",
                        "credit_cost": 8,
                        "requires_images": False,
                        "min_input_images": 0,
                        "max_input_images": 4,
                        "input_images_label": "Reference images",
                        "input_images_help": "Optional photo or sketch to guide the mesh.",
                        "default_positive": "clean topology, PBR textures, architectural prop",
                        "presets": [
                            {
                                "title": "Architectural prop",
                                "icon": "sparkles",
                                "positive": "furniture or decor object, watertight mesh, realistic materials",
                                "is_default": True,
                            },
                            {
                                "title": "From photo",
                                "icon": "image",
                                "positive": "match reference silhouette, quad-friendly topology",
                                "negative": "broken mesh, floating geometry",
                            },
                        ],
                    },
                    {
                        "slug": "meshy-lite-3d",
                        "name": "Meshy Lite",
                        "description": "Fast preview mesh from text",
                        "tag": "free",
                        "brand_icon": "meshy",
                        "provider": "meshy",
                        "external_id": "meshy-lite",
                        "credit_cost": 2,
                        "requires_images": False,
                        "min_input_images": 0,
                        "max_input_images": 1,
                        "input_images_label": "Reference image",
                        "input_images_help": "Optional single reference.",
                        "default_positive": "simple 3D object, low poly preview",
                        "presets": [
                            {
                                "title": "Quick blockout",
                                "icon": "sparkles",
                                "positive": "low poly blockout, readable silhouette",
                                "is_default": True,
                            },
                        ],
                    },
                    {
                        "slug": "tripo3d",
                        "name": "Tripo3D",
                        "description": "Tripo — high quality image/text to 3D",
                        "tag": "new",
                        "brand_icon": "tripo",
                        "provider": "tripo",
                        "external_id": "tripo-v2",
                        "credit_cost": 6,
                        "requires_images": False,
                        "min_input_images": 0,
                        "max_input_images": 4,
                        "input_images_label": "Reference images",
                        "input_images_help": "Optional front view or concept art.",
                        "default_positive": "detailed 3D asset, clean UVs, game-ready",
                        "presets": [
                            {
                                "title": "Product viz",
                                "icon": "sparkles",
                                "positive": "product hero object, studio lighting baked to texture",
                                "is_default": True,
                            },
                        ],
                    },
                    {
                        "slug": "rodin",
                        "name": "Rodin",
                        "description": "Hyperhuman Rodin — detailed organic & hard-surface 3D",
                        "tag": "pro",
                        "brand_icon": "rodin",
                        "provider": "hyperhuman",
                        "external_id": "rodin-v1",
                        "credit_cost": 10,
                        "requires_images": False,
                        "min_input_images": 0,
                        "max_input_images": 2,
                        "input_images_label": "Reference images",
                        "input_images_help": "Optional concept or orthographic references.",
                        "default_positive": "high detail sculpt, realistic proportions",
                        "presets": [
                            {
                                "title": "Character bust",
                                "icon": "sparkles",
                                "positive": "character bust, fine surface detail, production mesh",
                                "is_default": True,
                            },
                        ],
                    },
                    {
                        "slug": "hunyuan3d",
                        "name": "Hunyuan3D",
                        "description": "Tencent Hunyuan3D — fast text/image to mesh",
                        "tag": "new",
                        "brand_icon": "hunyuan",
                        "provider": "tencent",
                        "external_id": "hunyuan3d-v1",
                        "credit_cost": 5,
                        "requires_images": False,
                        "min_input_images": 0,
                        "max_input_images": 3,
                        "input_images_label": "Reference images",
                        "input_images_help": "Optional multi-view or single photo.",
                        "default_positive": "coherent 3D shape, consistent materials",
                        "presets": [
                            {
                                "title": "Scene object",
                                "icon": "sparkles",
                                "positive": "environment prop, stylized realism, export-ready",
                                "is_default": True,
                            },
                        ],
                    },
                    {
                        "slug": "luma-genie",
                        "name": "Luma Genie",
                        "description": "Luma — cinematic 3D from text or image",
                        "tag": "pro",
                        "brand_icon": "luma",
                        "provider": "luma",
                        "external_id": "genie-v1",
                        "credit_cost": 7,
                        "requires_images": False,
                        "min_input_images": 0,
                        "max_input_images": 2,
                        "input_images_label": "Reference image",
                        "input_images_help": "Optional image for image-to-3D.",
                        "default_positive": "cinematic 3D asset, smooth shading",
                        "presets": [
                            {
                                "title": "NeRF-style object",
                                "icon": "sparkles",
                                "positive": "single object, view-consistent, mesh export",
                                "is_default": True,
                            },
                        ],
                    },
                    {
                        "slug": "csm-ai",
                        "name": "CSM AI",
                        "description": "Common Sense Machines — image to 3D scene mesh",
                        "tag": "pro",
                        "brand_icon": "csm",
                        "provider": "csm",
                        "external_id": "csm-image-to-3d",
                        "credit_cost": 9,
                        "requires_images": True,
                        "min_input_images": 1,
                        "max_input_images": 1,
                        "input_images_label": "Source image",
                        "input_images_help": "One photo drives the 3D reconstruction.",
                        "default_positive": "scene reconstruction, depth-aware geometry",
                        "presets": [
                            {
                                "title": "Interior scan",
                                "icon": "sparkles",
                                "positive": "room-scale mesh, furniture separated, clean normals",
                                "is_default": True,
                            },
                        ],
                    },
                ],
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

        self.stdout.write(
            self.style.SUCCESS(
                f"Catalog seeded: {CapabilityCategory.objects.count()} categories, "
                f"{AIModel.objects.filter(is_active=True).count()} active models, "
                f"{CategoryPromptPreset.objects.filter(is_active=True).count()} category presets."
            )
        )
