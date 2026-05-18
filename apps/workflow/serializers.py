from rest_framework import serializers

from .models import Workflow


class WorkflowSerializer(serializers.ModelSerializer):
    project_id = serializers.UUIDField(source="project.id", read_only=True)
    flow_data = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = (
            "id",
            "project_id",
            "name",
            "graph",
            "flow_data",
            "version",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "version", "created_at", "updated_at")

    def get_flow_data(self, obj: Workflow) -> dict:
        return obj.graph


class WorkflowSaveSerializer(serializers.Serializer):
    graph = serializers.JSONField(required=False)
    flow_data = serializers.JSONField(required=False)
    name = serializers.CharField(required=False, max_length=255)

    def validate(self, attrs):
        flow = attrs.get("flow_data") or attrs.get("graph")
        if flow is None:
            raise serializers.ValidationError(
                {"graph": "Provide graph or flow_data."}
            )
        if not isinstance(flow, dict):
            raise serializers.ValidationError("flow_data must be an object.")
        if "nodes" not in flow:
            flow["nodes"] = []
        if "edges" not in flow:
            flow["edges"] = []
        attrs["graph"] = flow
        return attrs
