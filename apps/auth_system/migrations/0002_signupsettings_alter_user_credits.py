from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth_system", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SignupSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "free_signup_credits",
                    models.PositiveIntegerField(
                        default=5,
                        help_text="Credits given when a user registers (admin-managed).",
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "signup settings",
                "verbose_name_plural": "signup settings",
                "db_table": "signup_settings",
            },
        ),
        migrations.AlterField(
            model_name="user",
            name="credits",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Set automatically on registration from Signup settings.",
            ),
        ),
        migrations.RunPython(
            lambda apps, schema_editor: apps.get_model("auth_system", "SignupSettings").objects.get_or_create(
                pk=1,
                defaults={"free_signup_credits": 5},
            ),
            migrations.RunPython.noop,
        ),
    ]
