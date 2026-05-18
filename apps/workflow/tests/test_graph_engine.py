from django.test import SimpleTestCase

from apps.workflow.graph_engine import FlowGraphExecutor, GraphExecutionError, execute_flow_graph

EXAMPLE_FLOW = {
    "nodes": [
        {
            "id": "node_prompt_1",
            "type": "text_prompt",
            "data": {"text": "Modern villa"},
        },
        {
            "id": "node_model_1",
            "type": "ai_model",
            "data": {"model_name": "Flux v1.1", "aspect_ratio": "16:9", "steps": 30},
        },
        {
            "id": "node_output_1",
            "type": "image_output",
            "data": {"url": None},
        },
    ],
    "edges": [
        {
            "id": "edge_1",
            "source": "node_prompt_1",
            "sourceHandle": "output",
            "target": "node_model_1",
            "targetHandle": "prompt_input",
        },
        {
            "id": "edge_2",
            "source": "node_model_1",
            "sourceHandle": "image_output",
            "target": "node_output_1",
            "targetHandle": "input",
        },
    ],
}


class FlowGraphExecutorTests(SimpleTestCase):
    def test_root_nodes(self):
        ex = FlowGraphExecutor(EXAMPLE_FLOW)
        self.assertEqual(ex.root_nodes(), ["node_prompt_1"])

    def test_topological_order(self):
        ex = FlowGraphExecutor(EXAMPLE_FLOW)
        order = ex.topological_order()
        self.assertEqual(order[0], "node_prompt_1")
        self.assertEqual(order[-1], "node_output_1")

    def test_execute_sets_output_url(self):
        updated, statuses = execute_flow_graph(EXAMPLE_FLOW)
        output_node = next(n for n in updated["nodes"] if n["id"] == "node_output_1")
        self.assertTrue(output_node["data"]["url"])
        self.assertEqual(statuses["node_output_1"], "completed")

    def test_cycle_raises(self):
        cyclic = {
            "nodes": [
                {"id": "a", "type": "text_prompt", "data": {"text": "x"}},
                {"id": "b", "type": "ai_model", "data": {}},
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "a",
                    "sourceHandle": "output",
                    "target": "b",
                    "targetHandle": "prompt_input",
                },
                {
                    "id": "e2",
                    "source": "b",
                    "sourceHandle": "image_output",
                    "target": "a",
                    "targetHandle": "prompt_input",
                },
            ],
        }
        with self.assertRaises(GraphExecutionError):
            FlowGraphExecutor(cyclic).topological_order()
