import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_categorypromptpreset"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserPromptPreset",
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
                ("title", models.CharField(max_length=128)),
                ("icon", models.CharField(blank=True, default="sparkles", max_length=64)),
                ("positive_prompt", models.TextField()),
                ("negative_prompt", models.TextField(blank=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_prompt_presets",
                        to="catalog.capabilitycategory",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prompt_presets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "user_prompt_presets",
                "ordering": ["sort_order", "-created_at"],
                "indexes": [
                    models.Index(
                        fields=["user", "category"],
                        name="user_prompt_user_id_categ_idx",
                    )
                ],
            },
        ),
    ]
