from rest_framework import serializers

from .models import Project
from .utils import node_count_from_graph, preview_url_from_graph


class ProjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "thumbnail",
            "is_template",
            "last_activity_summary",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "last_activity_summary")


class ProjectListSerializer(serializers.ModelSerializer):
    workflow_id = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    node_count = serializers.SerializerMethodField()
    last_activity_label = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "thumbnail",
            "is_template",
            "workflow_id",
            "preview_url",
            "node_count",
            "last_activity_label",
            "last_activity_summary",
            "created_at",
            "updated_at",
        )

    def _workflow(self, obj: Project):
        workflows = getattr(obj, "_workflows", None)
        if workflows:
            return workflows[0]
        return obj.workflows.first()

    def get_workflow_id(self, obj):
        wf = self._workflow(obj)
        return str(wf.id) if wf else None

    def get_preview_url(self, obj):
        if obj.thumbnail:
            try:
                return obj.thumbnail.url
            except Exception:
                pass
        wf = self._workflow(obj)
        if wf:
            url = preview_url_from_graph(wf.graph)
            if url:
                return url
        preview_by_project = self.context.get("preview_by_project") or {}
        return preview_by_project.get(str(obj.id))

    def get_node_count(self, obj):
        wf = self._workflow(obj)
        if wf:
            return node_count_from_graph(wf.graph)
        return 0

    def get_last_activity_label(self, obj):
        if obj.last_activity_summary:
            return obj.last_activity_summary
        return "Project created"
