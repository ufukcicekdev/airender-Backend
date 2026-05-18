import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_aimodel_brand_icon_aimodel_tag"),
    ]

    operations = [
        migrations.CreateModel(
            name="CategoryPromptPreset",
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
                ("slug", models.SlugField(blank=True, max_length=64)),
                ("title", models.CharField(max_length=128)),
                ("icon", models.CharField(blank=True, max_length=64)),
                ("positive_prompt", models.TextField()),
                ("negative_prompt", models.TextField(blank=True)),
                ("is_default", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prompt_presets",
                        to="catalog.capabilitycategory",
                    ),
                ),
            ],
            options={
                "db_table": "category_prompt_presets",
                "ordering": ["sort_order", "title"],
                "unique_together": {("category", "slug")},
            },
        ),
    ]
