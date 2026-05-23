from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="last_activity_summary",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Short label for dashboard (e.g. Generation completed)",
                max_length=128,
            ),
        ),
    ]
