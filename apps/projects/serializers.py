from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "thumbnail",
            "is_template",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ProjectListSerializer(serializers.ModelSerializer):
    workflow_id = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "thumbnail",
            "is_template",
            "workflow_id",
            "created_at",
            "updated_at",
        )

    def get_workflow_id(self, obj):
        workflows = getattr(obj, "_workflows", None) or obj.workflows.all()[:1]
        wf = workflows[0] if workflows else obj.workflows.first()
        return str(wf.id) if wf else None
