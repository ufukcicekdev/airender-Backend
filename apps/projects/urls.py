from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet

# Register under "projects" so /api/projects and /api/projects/<id> both resolve
# (empty prefix under path("api/projects/") broke detail routes; trailing slash breaks POST via proxy)
router = DefaultRouter(trailing_slash=False)
router.register(r"projects", ProjectViewSet, basename="project")

urlpatterns = [
    path("", include(router.urls)),
]
