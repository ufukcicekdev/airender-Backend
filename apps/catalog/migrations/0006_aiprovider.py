import uuid

from django.db import migrations, models


def seed_providers(apps, schema_editor):
    AIProvider = apps.get_model("catalog", "AIProvider")
    rows = [
        ("fal", "Fal.ai", "https://queue.fal.run", "FAL_API_KEY", "fal", "", True, 0),
        ("comfy", "ComfyUI", "", "COMFYUI_URL", "comfy", "prompt", False, 1),
        ("replicate", "Replicate", "https://api.replicate.com/v1", "REPLICATE_API_TOKEN", "http", "", False, 2),
        ("openai", "OpenAI", "https://api.openai.com/v1", "OPENAI_API_KEY", "http", "images/edits", False, 3),
        ("magnific", "Magnific", "https://api.magnific.ai/v1", "MAGNIFIC_API_KEY", "http", "upscale", False, 4),
        ("bytedance", "ByteDance", "https://api.byteplus.com/v1", "BYTEDANCE_API_KEY", "http", "", False, 5),
        ("meshy", "Meshy 3D", "https://api.meshy.ai/v2", "MESHY_API_KEY", "http", "text-to-3d", False, 10),
        ("tripo", "Tripo 3D", "https://api.tripo3d.ai/v2", "TRIPO_API_KEY", "http", "openapi/task", False, 11),
        ("hyperhuman", "Hyperhuman", "https://api.hyperhuman.ai/v1", "HYPERHUMAN_API_KEY", "http", "generate", False, 12),
        ("tencent", "Tencent Hunyuan", "https://hunyuan.tencentcloudapi.com", "TENCENT_AI_API_KEY", "http", "3d/generate", False, 13),
        ("luma", "Luma AI", "https://api.lumalabs.ai/dream-machine/v1", "LUMA_API_KEY", "http", "generations", False, 14),
        ("csm", "CSM", "https://api.csm.ai/v1", "CSM_API_KEY", "http", "image-to-3d", False, 15),
    ]
    for slug, name, base_url, env_var, adapter, default_path, use_ext, order in rows:
        AIProvider.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "base_url": base_url,
                "api_key_env_var": env_var,
                "adapter": adapter,
                "default_path": default_path,
                "use_external_id_as_path": use_ext,
                "is_active": True,
                "sort_order": order,
            },
        )
    # Fal-style path resolution
    AIProvider.objects.filter(slug="fal").update(use_external_id_as_path=True)


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0005_userpromptpreset"),
    ]

    operations = [
        migrations.CreateModel(
            name="AIProvider",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("slug", models.SlugField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=128)),
                ("base_url", models.URLField(blank=True, max_length=512)),
                ("api_key_env_var", models.CharField(blank=True, max_length=128)),
                (
                    "adapter",
                    models.CharField(
                        choices=[
                            ("fal", "Fal queue API"),
                            ("comfy", "ComfyUI"),
                            ("http", "Generic HTTP (Bearer)"),
                            ("stub", "Development stub"),
                        ],
                        default="http",
                        max_length=32,
                    ),
                ),
                ("default_path", models.CharField(blank=True, max_length=256)),
                ("path_template", models.CharField(blank=True, max_length=256)),
                ("use_external_id_as_path", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "ai_providers",
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.RunPython(seed_providers, migrations.RunPython.noop),
    ]
