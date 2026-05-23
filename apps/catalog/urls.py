from django.urls import path
from rest_framework.routers import DefaultRouter

from .credit_estimate_views import CreditEstimateView
from .views import CatalogView, UserPromptPresetViewSet

router = DefaultRouter(trailing_slash=False)
router.register("my-presets", UserPromptPresetViewSet, basename="user-preset")

urlpatterns = [
    path("", CatalogView.as_view(), name="catalog"),
    path("estimate-credits", CreditEstimateView.as_view(), name="catalog-estimate-credits"),
    *router.urls,
]
