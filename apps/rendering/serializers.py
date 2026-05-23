from rest_framework import serializers

from apps.core.media_urls import public_media_url

from .models import GeneratedImage, RenderTask


class GeneratedImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedImage
        fields = (
            "id",
            "image_url",
            "thumbnail_url",
            "width",
            "height",
            "metadata",
            "created_at",
        )

    def get_image_url(self, obj):
        return public_media_url(obj.image)

    def get_thumbnail_url(self, obj):
        return public_media_url(obj.thumbnail)


class RenderTaskSerializer(serializers.ModelSerializer):
    images = GeneratedImageSerializer(many=True, read_only=True)
    flow_data = serializers.SerializerMethodField()

    class Meta:
        model = RenderTask
        fields = (
            "id",
            "workflow",
            "status",
            "progress",
            "current_stage",
            "node_statuses",
            "error_message",
            "images",
            "flow_data",
            "created_at",
            "started_at",
            "completed_at",
        )
        read_only_fields = fields

    def get_flow_data(self, obj: RenderTask) -> dict:
        if obj.workflow_id:
            return obj.workflow.graph or {}
        return {}


class StartRenderSerializer(serializers.Serializer):
    workflow_id = serializers.UUIDField()
    node_id = serializers.CharField(required=False, allow_blank=True)
    category_slug = serializers.CharField(required=False, allow_blank=True)
    model_slug = serializers.CharField(required=False, allow_blank=True)
