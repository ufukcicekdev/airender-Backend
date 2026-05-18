"""
Directed Acyclic Graph (DAG) executor for node-based flows.

Reads Workflow.graph / flow_data JSON:
  { "nodes": [...], "edges": [...] }

Supported node types:
  - text_prompt  → output handle "output" (str)
  - ai_model     → input "prompt_input", output "image_output" (url)
  - image_output → input "input" (url written to node.data.url)
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable

from apps.rendering.providers import RenderJob, resolve_ai_model, run_provider


class GraphExecutionError(Exception):
    """Raised when the flow graph is invalid or execution fails."""


@dataclass
class NodeExecutionResult:
    node_id: str
    outputs: dict[str, Any] = field(default_factory=dict)
    status: str = "completed"
    error: str | None = None


class FlowGraphExecutor:
    """Parse and execute a React Flow graph as a DAG."""

    SUPPORTED_TYPES = frozenset({"text_prompt", "ai_model", "image_output"})

    def __init__(
        self,
        flow_data: dict[str, Any],
        *,
        on_progress: Callable[[int, str], None] | None = None,
    ):
        self.flow_data = flow_data
        self.on_progress = on_progress
        self.nodes: dict[str, dict] = {
            n["id"]: n for n in flow_data.get("nodes", []) if n.get("id")
        }
        self.edges: list[dict] = list(flow_data.get("edges", []))
        self.incoming: dict[str, list[dict]] = defaultdict(list)
        self.outgoing: dict[str, list[dict]] = defaultdict(list)
        self.values: dict[str, dict[str, Any]] = {}
        self.node_statuses: dict[str, str] = {}

        for edge in self.edges:
            src, tgt = edge.get("source"), edge.get("target")
            if not src or not tgt:
                continue
            if src not in self.nodes or tgt not in self.nodes:
                raise GraphExecutionError(
                    f"Edge references unknown node: {edge.get('id', '?')}"
                )
            self.outgoing[src].append(edge)
            self.incoming[tgt].append(edge)

    # ------------------------------------------------------------------ parse
    def root_nodes(self) -> list[str]:
        """Nodes that are never a target of any edge."""
        targets = {e["target"] for e in self.edges if e.get("target")}
        return [nid for nid in self.nodes if nid not in targets]

    def topological_order(self) -> list[str]:
        """Kahn's algorithm — raises if cycle detected."""
        in_degree = {nid: len(self.incoming[nid]) for nid in self.nodes}
        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        order: list[str] = []

        while queue:
            nid = queue.popleft()
            order.append(nid)
            for edge in self.outgoing.get(nid, []):
                tgt = edge["target"]
                in_degree[tgt] -= 1
                if in_degree[tgt] == 0:
                    queue.append(tgt)

        if len(order) != len(self.nodes):
            raise GraphExecutionError("Flow graph contains a cycle.")
        return order

    def get_input_value(self, node_id: str, target_handle: str) -> Any:
        """Resolve value arriving at target_handle on node_id."""
        for edge in self.incoming.get(node_id, []):
            if edge.get("targetHandle") != target_handle:
                continue
            source_id = edge["source"]
            source_handle = edge.get("sourceHandle") or "output"
            source_outputs = self.values.get(source_id, {})
            if source_handle in source_outputs:
                return source_outputs[source_handle]
            if "output" in source_outputs:
                return source_outputs["output"]
        return None

    # -------------------------------------------------------------- execution
    def execute(self) -> dict[str, Any]:
        """
        Run the full DAG. Returns updated flow_data with mutated node.data
        and a parallel node_statuses map.
        """
        if not self.nodes:
            raise GraphExecutionError("Flow graph has no nodes.")

        order = self.topological_order()
        for node_id in order:
            node = self.nodes[node_id]
            ntype = node.get("type", "")
            self.node_statuses[node_id] = "processing"
            try:
                if ntype not in self.SUPPORTED_TYPES:
                    raise GraphExecutionError(f"Unsupported node type: {ntype}")
                result = self._execute_node(node)
                self.values[node_id] = result.outputs
                self.node_statuses[node_id] = result.status
                if result.error:
                    self.node_statuses[node_id] = "error"
                    raise GraphExecutionError(result.error)
            except GraphExecutionError:
                self.node_statuses[node_id] = "error"
                raise
            except Exception as exc:
                self.node_statuses[node_id] = "error"
                raise GraphExecutionError(str(exc)) from exc

        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
        }

    def _execute_node(self, node: dict) -> NodeExecutionResult:
        ntype = node["type"]
        data = node.setdefault("data", {})
        node_id = node["id"]

        if ntype == "text_prompt":
            text = data.get("text") or data.get("label") or ""
            return NodeExecutionResult(
                node_id=node_id,
                outputs={"output": text},
            )

        if ntype == "ai_model":
            prompt = self.get_input_value(node_id, "prompt_input")
            if prompt is None:
                prompt = data.get("prompt") or data.get("text") or ""
            image_url = self._run_ai_model(data, str(prompt))
            data["last_output_url"] = image_url
            return NodeExecutionResult(
                node_id=node_id,
                outputs={"image_output": image_url},
            )

        if ntype == "image_output":
            url = self.get_input_value(node_id, "input")
            data["url"] = url
            return NodeExecutionResult(
                node_id=node_id,
                outputs={"input": url},
            )

        return NodeExecutionResult(
            node_id=node_id,
            status="error",
            error=f"Unhandled type {ntype}",
        )

    def _run_ai_model(self, data: dict[str, Any], prompt: str) -> str:
        category_slug = str(data.get("categorySlug") or "")
        model_slug = str(data.get("modelSlug") or "")
        model = resolve_ai_model(category_slug, model_slug)

        output_type = "video" if category_slug == "image-to-video" else "image"

        job = RenderJob(
            prompt=prompt,
            negative_prompt=str(data.get("negative") or ""),
            model_slug=model_slug,
            category_slug=category_slug,
            model_name=str(data.get("model_name") or "AI Model"),
            output_type=output_type,
            source_image_urls=list(data.get("source_image_urls") or []),
            settings={
                "aspect_ratio": data.get("aspect_ratio", "1:1"),
                "steps": int(data.get("steps", 30)),
                "priority": data.get("priority"),
                "resolution": data.get("resolution"),
                "upscale_scale": data.get("upscale_scale"),
                "max_output": data.get("max_output"),
            },
        )

        if model is None:
            from types import SimpleNamespace

            from apps.rendering.providers.stub import StubAdapter

            fallback = SimpleNamespace(
                name=job.model_name,
                slug=model_slug or "default",
                provider="stub",
            )
            return StubAdapter().run(
                fallback, job, on_progress=self.on_progress
            )

        return run_provider(model, job, on_progress=self.on_progress)


def execute_flow_graph(
    flow_data: dict[str, Any],
    *,
    on_progress: Callable[[int, str], None] | None = None,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Convenience entry: returns (updated_flow_data, node_statuses)."""
    executor = FlowGraphExecutor(flow_data, on_progress=on_progress)
    updated = executor.execute()
    return updated, executor.node_statuses
