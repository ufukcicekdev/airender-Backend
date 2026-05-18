import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY", default="dev-insecure-key")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
_railway_public = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").strip()
if _railway_public and _railway_public not in ALLOWED_HOSTS:
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, _railway_public]

INSTALLED_APPS = [
    "jazzmin",
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "django_celery_beat",
    "channels",
    "apps.auth_system",
    "apps.projects",
    "apps.workflow",
    "apps.rendering",
    "apps.assets",
    "apps.billing",
    "apps.catalog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

def _configure_databases():
    engine = env("DATABASE_ENGINE", default="")
    if engine:
        db = {
            "ENGINE": engine,
            "NAME": env("DATABASE_NAME"),
            "USER": env("DATABASE_USER"),
            "PASSWORD": env("DATABASE_PASSWORD"),
            "HOST": env("DATABASE_HOST"),
            "PORT": env("DATABASE_PORT", default="5432"),
            "CONN_MAX_AGE": 600,
        }
        sslmode = env("DATABASE_SSLMODE", default="")
        if sslmode:
            db["OPTIONS"] = {"sslmode": sslmode}
        return {"default": db}

    return {
        "default": dj_database_url.config(
            default=env("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
            conn_max_age=600,
        )
    }


DATABASES = _configure_databases()

AUTH_USER_MODEL = "auth_system.User"

AUTHENTICATION_BACKENDS = [
    "apps.auth_system.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
USE_S3 = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Admin UI (django-jazzmin) — must load after INSTALLED_APPS defines apps
from config.jazzmin_settings import JAZZMIN_SETTINGS, JAZZMIN_UI_TWEAKS  # noqa: E402, F401

# Object storage (DigitalOcean Spaces / S3) — see config/storage.py
from config.storage import s3_storage_settings  # noqa: E402

_s3 = s3_storage_settings(env)
if _s3:
    _apps_extra = _s3.pop("_INSTALLED_APPS_APPEND", [])
    for _key, _val in _s3.items():
        globals()[_key] = _val
    if _apps_extra:
        INSTALLED_APPS = [*INSTALLED_APPS, *_apps_extra]

# CORS — allow localhost + 127.0.0.1 (browser may use either)
_default_cors = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=_default_cors)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
CORS_EXPOSE_HEADERS = ["Content-Type", "X-Request-ID"]

if DEBUG:
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^http://localhost:\d+$",
        r"^http://127\.0\.0\.1:\d+$",
    ]

FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")

_csrf_origins = list(
    dict.fromkeys(
        CORS_ALLOWED_ORIGINS
        + [FRONTEND_URL, "http://127.0.0.1:3000", "http://localhost:3000"]
    )
)
if _railway_public:
    _csrf_origins.append(f"https://{_railway_public}")
CSRF_TRUSTED_ORIGINS = _csrf_origins

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "apps.auth_system.authentication.CookieJWTAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/hour", "user": "1000/hour"},
}

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

JWT_COOKIE_ACCESS = "access_token"
JWT_COOKIE_REFRESH = "refresh_token"
JWT_COOKIE_SECURE = not DEBUG
JWT_COOKIE_HTTPONLY = True
JWT_COOKIE_SAMESITE = "Lax"
JWT_COOKIE_PATH = "/"

# Email
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@vizmake.local")

# Redis & Channels
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}

# Celery
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_ROUTES = {
    "apps.rendering.tasks.*": {"queue": "rendering"},
}

# Public URL for WebSocket media links (must match what the browser can load)
BACKEND_PUBLIC_URL = env("BACKEND_PUBLIC_URL", default="http://localhost:8000")

# AI providers (internal router — Comfy primary, direct APIs per model)
COMFYUI_URL = env("COMFYUI_URL", default="")
FAL_API_BASE = env("FAL_API_BASE", default="https://queue.fal.run")
FAL_API_KEY = env("FAL_API_KEY", default="")
REPLICATE_API_BASE = env("REPLICATE_API_BASE", default="https://api.replicate.com/v1")
REPLICATE_API_TOKEN = env("REPLICATE_API_TOKEN", default="")
OPENAI_API_BASE = env("OPENAI_API_BASE", default="https://api.openai.com/v1")
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
MAGNIFIC_API_BASE = env("MAGNIFIC_API_BASE", default="https://api.magnific.ai/v1")
MAGNIFIC_API_KEY = env("MAGNIFIC_API_KEY", default="")
RUNWAY_API_BASE = env("RUNWAY_API_BASE", default="https://api.runwayml.com/v1")
RUNWAY_API_KEY = env("RUNWAY_API_KEY", default="")
GOOGLE_AI_API_BASE = env(
    "GOOGLE_AI_API_BASE", default="https://generativelanguage.googleapis.com/v1beta"
)
GOOGLE_AI_API_KEY = env("GOOGLE_AI_API_KEY", default="")
KLING_API_BASE = env("KLING_API_BASE", default="https://api.klingai.com/v1")
KLING_API_KEY = env("KLING_API_KEY", default="")
BYTEDANCE_API_BASE = env("BYTEDANCE_API_BASE", default="https://api.byteplus.com/v1")
BYTEDANCE_API_KEY = env("BYTEDANCE_API_KEY", default="")
# 3D model services (catalog category 3d-model)
MESHY_API_BASE = env("MESHY_API_BASE", default="https://api.meshy.ai/v2")
MESHY_API_KEY = env("MESHY_API_KEY", default="")
TRIPO_API_BASE = env("TRIPO_API_BASE", default="https://api.tripo3d.ai/v2")
TRIPO_API_KEY = env("TRIPO_API_KEY", default="")
HYPERHUMAN_API_BASE = env("HYPERHUMAN_API_BASE", default="https://api.hyperhuman.ai/v1")
HYPERHUMAN_API_KEY = env("HYPERHUMAN_API_KEY", default="")
TENCENT_AI_API_BASE = env("TENCENT_AI_API_BASE", default="https://hunyuan.tencentcloudapi.com")
TENCENT_AI_API_KEY = env("TENCENT_AI_API_KEY", default="")
LUMA_API_BASE = env("LUMA_API_BASE", default="https://api.lumalabs.ai/dream-machine/v1")
LUMA_API_KEY = env("LUMA_API_KEY", default="")
CSM_API_BASE = env("CSM_API_BASE", default="https://api.csm.ai/v1")
CSM_API_KEY = env("CSM_API_KEY", default="")
ENABLE_FAL_FALLBACK = env.bool("ENABLE_FAL_FALLBACK", default=False)

# File uploads
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
