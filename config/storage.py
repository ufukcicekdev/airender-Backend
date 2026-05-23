"""DigitalOcean Spaces / S3-compatible object storage (optional)."""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ImproperlyConfigured


def s3_storage_settings(env) -> dict[str, Any] | None:
    """
    Return settings dict to merge into config.settings when S3 is enabled.
    Returns None for local filesystem storage.
    """
    bucket = env("AWS_STORAGE_BUCKET_NAME", default="")
    use_s3 = env.bool("USE_S3", default=bool(bucket))
    require_s3 = env.bool("REQUIRE_S3_STORAGE", default=use_s3)

    if not use_s3:
        return None

    if not bucket:
        msg = "USE_S3=1 but AWS_STORAGE_BUCKET_NAME is not set."
        if require_s3:
            raise ImproperlyConfigured(msg)
        return None

    access_key = env("AWS_ACCESS_KEY_ID", default="")
    secret_key = env("AWS_SECRET_ACCESS_KEY", default="")
    if not access_key or not secret_key:
        msg = (
            "USE_S3=1 but AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY are missing. "
            "Uploads and Fal outputs will not reach Spaces."
        )
        if require_s3:
            raise ImproperlyConfigured(msg)
        return None

    region = env("AWS_S3_REGION_NAME", default="fra1")
    endpoint = env(
        "AWS_S3_ENDPOINT_URL",
        default=f"https://{region}.digitaloceanspaces.com",
    )
    location = env("AWS_LOCATION", default="vizmake").strip("/")
    custom_domain = env("AWS_S3_CUSTOM_DOMAIN", default="").strip()
    if not custom_domain:
        custom_domain = f"{bucket}.{region}.digitaloceanspaces.com"

    media_url = (
        f"https://{custom_domain}/{location}/"
        if location
        else f"https://{custom_domain}/"
    )

    return {
        "USE_S3": True,
        "AWS_ACCESS_KEY_ID": access_key,
        "AWS_SECRET_ACCESS_KEY": secret_key,
        "AWS_STORAGE_BUCKET_NAME": bucket,
        "AWS_S3_REGION_NAME": region,
        "AWS_S3_ENDPOINT_URL": endpoint,
        "AWS_S3_SIGNATURE_VERSION": "s3v4",
        "AWS_S3_ADDRESSING_STYLE": env("AWS_S3_ADDRESSING_STYLE", default="virtual"),
        "AWS_S3_FILE_OVERWRITE": False,
        "AWS_DEFAULT_ACL": env("AWS_DEFAULT_ACL", default="public-read"),
        "AWS_QUERYSTRING_AUTH": env.bool("AWS_QUERYSTRING_AUTH", default=False),
        "AWS_LOCATION": location,
        "AWS_S3_OBJECT_PARAMETERS": {
            "CacheControl": env("AWS_S3_CACHE_CONTROL", default="max-age=86400"),
        },
        "AWS_S3_CUSTOM_DOMAIN": custom_domain,
        "MEDIA_URL": media_url,
        "STORAGES": {
            "default": {
                "BACKEND": "storages.backends.s3.S3Storage",
            },
            "staticfiles": {
                "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
            },
        },
        "_INSTALLED_APPS_APPEND": ["storages"],
    }
