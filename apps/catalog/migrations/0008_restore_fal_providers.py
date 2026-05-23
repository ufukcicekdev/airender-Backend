"""Re-enable Fal.ai as the primary provider for catalog models."""

from django.db import migrations

FAL_MODEL_SLUGS = [
    "nano-banana-2",
    "nano-banana-pro",
    "nano-banana",
    "veo-3-1",
    "kling-pro",
    "seedance",
    "runway-gen3",
    "seedream",
    "flux-pro",
    "gpt-image",
    "gpt-image-2",
]


def forwards(apps, schema_editor):
    AIProvider = apps.get_model("catalog", "AIProvider")
    AIModel = apps.get_model("catalog", "AIModel")

    AIProvider.objects.filter(slug="fal").update(is_active=True)
    AIProvider.objects.filter(slug="google").update(is_active=False)

    AIModel.objects.filter(slug__in=FAL_MODEL_SLUGS).update(provider="fal")


def backwards(apps, schema_editor):
    AIProvider = apps.get_model("catalog", "AIProvider")
    AIModel = apps.get_model("catalog", "AIModel")

    AIProvider.objects.filter(slug="fal").update(is_active=False)
    AIProvider.objects.filter(slug="google").update(is_active=True)

    mapping = {
        "nano-banana-2": "google",
        "nano-banana-pro": "google",
        "nano-banana": "google",
        "veo-3-1": "google",
        "kling-pro": "kling",
        "seedance": "bytedance",
        "runway-gen3": "runway",
        "seedream": "bytedance",
    }
    for slug, provider in mapping.items():
        AIModel.objects.filter(slug=slug).update(provider=provider)


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0007_reassign_fal_providers"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
