from rest_framework import serializers

from apps.core.media_urls import public_media_url

from .models import Asset


class AssetSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = (
            "id",
            "name",
            "file_url",
            "thumbnail_url",
            "width",
            "height",
            "file_size",
            "created_at",
        )
        read_only_fields = ("id", "width", "height", "file_size", "created_at")

    def get_file_url(self, obj):
        return public_media_url(obj.file)

    def get_thumbnail_url(self, obj):
        return public_media_url(obj.thumbnail)
