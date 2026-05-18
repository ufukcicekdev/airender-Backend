from django.test import SimpleTestCase

from apps.workflow.flow_builder import build_execution_flow_from_canvas


class FlowBuilderTests(SimpleTestCase):
    def test_builds_dag_from_source_and_render(self):
        canvas = {
            "nodes": [
                {"id": "src1", "type": "source", "data": {"imageUrl": "http://x"}},
                {
                    "id": "rend1",
                    "type": "render",
                    "data": {
                        "positive": "Modern villa",
                        "model_name": "Flux v1.1",
                        "aspect_ratio": "16:9",
                        "steps": 30,
                    },
                },
            ],
            "edges": [{"id": "e1", "source": "src1", "target": "rend1"}],
        }
        built = build_execution_flow_from_canvas(canvas, "rend1")
        self.assertIsNotNone(built)
        types = [n["type"] for n in built["nodes"]]
        self.assertEqual(types, ["text_prompt", "ai_model", "image_output"])
        self.assertEqual(built["_target_render_id"], "rend1")
