from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config.health import health_check

urlpatterns = [
    path("api/health/", health_check),
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.auth_system.urls")),
    # No trailing slash — pairs with DefaultRouter(trailing_slash=False) to avoid 301 loops
    path("api/projects", include("apps.projects.urls")),
    path("api/workflow/", include("apps.workflow.urls")),
    path("api/render/", include("apps.rendering.urls")),
    path("api/assets/", include("apps.assets.urls")),
    path("api/billing", include("apps.billing.urls")),
    path("api/catalog", include("apps.catalog.urls")),
]

if settings.DEBUG and not getattr(settings, "USE_S3", False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
