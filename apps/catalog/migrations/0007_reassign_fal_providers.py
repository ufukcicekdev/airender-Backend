"""Deactivate Fal.ai and reassign catalog models to direct API providers."""

from django.db import migrations

PROVIDER_BY_SLUG = {
    "nano-banana-2": "google",
    "nano-banana-pro": "google",
    "nano-banana": "google",
    "veo-3-1": "google",
    "kling-pro": "kling",
    "seedance": "bytedance",
    "runway-gen3": "runway",
    "seedream": "bytedance",
}


def forwards(apps, schema_editor):
    AIProvider = apps.get_model("catalog", "AIProvider")
    AIModel = apps.get_model("catalog", "AIModel")

    extra_providers = [
        ("google", "Google AI", "https://generativelanguage.googleapis.com/v1beta", "GOOGLE_AI_API_KEY", "http", "", False, 6),
        ("kling", "Kling AI", "https://api.klingai.com/v1", "KLING_API_KEY", "http", "videos/image2video", False, 7),
        ("runway", "Runway", "https://api.runwayml.com/v1", "RUNWAY_API_KEY", "http", "image_to_video", False, 8),
    ]
    for slug, name, base_url, env_var, adapter, default_path, use_ext, order in extra_providers:
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

    AIProvider.objects.filter(slug="fal").update(is_active=False)

    for slug, provider in PROVIDER_BY_SLUG.items():
        AIModel.objects.filter(slug=slug, provider="fal").update(provider=provider)
    AIModel.objects.filter(provider="fal").update(provider="google")


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0006_aiprovider"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
