from django.urls import path

from .views import AssetDetailView, AssetGalleryView, AssetUploadView

urlpatterns = [
    path("upload", AssetUploadView.as_view(), name="asset-upload"),
    path("gallery", AssetGalleryView.as_view(), name="asset-gallery"),
    path("<uuid:asset_id>", AssetDetailView.as_view(), name="asset-detail"),
]
