from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet

# No trailing slash — matches Next.js proxy and avoids POST redirect errors
router = DefaultRouter(trailing_slash=False)
router.register(r"", ProjectViewSet, basename="project")

urlpatterns = [
    path("", include(router.urls)),
]
