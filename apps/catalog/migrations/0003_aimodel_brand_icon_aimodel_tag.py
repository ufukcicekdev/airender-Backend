from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_aimodel_input_images_help_aimodel_input_images_label_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="aimodel",
            name="brand_icon",
            field=models.CharField(
                blank=True,
                help_text="Brand logo key for the frontend (flux, kling, gpt, …)",
                max_length=64,
            ),
        ),
        migrations.AddField(
            model_name="aimodel",
            name="tag",
            field=models.CharField(
                blank=True,
                choices=[
                    ("free", "Free"),
                    ("pro", "Pro"),
                    ("new", "New"),
                    ("beta", "Beta"),
                ],
                default="",
                help_text="Badge shown in the model picker (Free, Pro, New, …)",
                max_length=16,
            ),
        ),
    ]
