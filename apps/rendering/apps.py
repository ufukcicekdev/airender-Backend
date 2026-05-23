from django.apps import AppConfig


class RenderingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.rendering"
    label = "rendering"

    def ready(self) -> None:
        from apps.core.storage import assert_s3_ready, log_storage_status

        assert_s3_ready()
        log_storage_status()
