import logging

from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.media_urls import public_media_url
from apps.core.storage import use_s3_storage

from .models import Asset
from .serializers import AssetSerializer
from .services import generate_thumbnail, get_image_dimensions

logger = logging.getLogger(__name__)


class AssetUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file provided."}, status=400)

        asset = Asset(user=request.user, name=file.name, file=file)
        width, height = get_image_dimensions(file)
        asset.width = width
        asset.height = height
        asset.file_size = file.size

        thumb_buffer = generate_thumbnail(file)
        if thumb_buffer:
            asset.thumbnail.save(
                f"thumb_{file.name.rsplit('.', 1)[0]}.jpg",
                ContentFile(thumb_buffer.read()),
                save=False,
            )

        asset.save()
        file_url = public_media_url(asset.file)
        if use_s3_storage() and file_url and not file_url.startswith("https://"):
            logger.error("Asset saved but URL is not public HTTPS: %s", file_url)
            return Response(
                {"error": "Storage misconfigured — file was not saved to S3/Spaces."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        logger.info("Asset uploaded → %s", file_url)
        return Response(
            AssetSerializer(asset, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AssetGalleryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assets = Asset.objects.filter(user=request.user)
        return Response(
            AssetSerializer(assets, many=True, context={"request": request}).data
        )


class AssetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, asset_id):
        try:
            asset = Asset.objects.get(id=asset_id, user=request.user)
        except Asset.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        asset.file.delete(save=False)
        if asset.thumbnail:
            asset.thumbnail.delete(save=False)
        asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
