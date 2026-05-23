"""
Build a spec DAG (text_prompt → ai_model → image_output) from Vizmaker-style
canvas nodes (source + render). Users never add flow nodes manually.
"""

from __future__ import annotations

import uuid
from typing import Any

FLOW_TYPES = frozenset({"text_prompt", "ai_model", "image_output"})
CANVAS_RENDER_TYPES = frozenset({"render", "detail"})


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def build_execution_flow_from_canvas(
    graph: dict[str, Any],
    render_node_id: str | None = None,
) -> dict[str, Any] | None:
    """
    Return a standalone DAG for Celery, or None if no render node to run.
    Keys: nodes, edges, _execution_output_id (internal).
    """
    nodes: list[dict] = list(graph.get("nodes") or [])
    edges: list[dict] = list(graph.get("edges") or [])
    node_by_id = {n["id"]: n for n in nodes if n.get("id")}

    render_node = None
    if render_node_id and render_node_id in node_by_id:
        candidate = node_by_id[render_node_id]
        if candidate.get("type") in CANVAS_RENDER_TYPES:
            render_node = candidate

    if not render_node:
        for n in nodes:
            if n.get("type") in CANVAS_RENDER_TYPES:
                render_node = n
                break

    if not render_node:
        return None

    rid = render_node["id"]
    data = render_node.get("data") or {}

    source_ids = [
        e["source"]
        for e in edges
        if e.get("target") == rid
        and e.get("source") in node_by_id
        and node_by_id[e["source"]].get("type") == "source"
    ]
    source_image_urls: list[str] = []
    for sid in source_ids:
        url = (node_by_id[sid].get("data") or {}).get("imageUrl")
        if url and isinstance(url, str):
            source_image_urls.append(url)

    prompt = (
        data.get("positive")
        or data.get("prompt")
        or data.get("text")
        or "Create photorealistic image"
    )
    negative = data.get("negative") or ""
    model_name = data.get("model_name") or data.get("modelSlug") or "Flux v1.1"
    model_slug = str(data.get("modelSlug") or "")
    category_slug = str(data.get("categorySlug") or "")
    aspect_ratio = data.get("aspect_ratio") or "16:9"
    steps = int(data.get("steps") or 30)
    priority = data.get("priority")
    resolution = data.get("resolution")
    video_duration = data.get("video_duration") or data.get("videoDuration")
    generate_audio = data.get("generate_audio")
    upscale_scale = data.get("upscaleScale") or data.get("upscale_scale")
    max_output = data.get("upscaleMaxOutput") or data.get("max_output")

    ref_note = f" [refs: {len(source_ids)} source(s)]" if source_ids else ""

    prompt_id = _new_id("node_prompt")
    model_id = _new_id("node_model")
    output_id = _new_id("node_output")

    flow_nodes = [
        {
            "id": prompt_id,
            "type": "text_prompt",
            "data": {"text": f"{prompt}{ref_note}", "negative": negative},
        },
        {
            "id": model_id,
            "type": "ai_model",
            "data": {
                "model_name": str(model_name),
                "modelSlug": model_slug,
                "categorySlug": category_slug,
                "aspect_ratio": str(aspect_ratio),
                "steps": steps,
                "prompt": str(prompt),
                "negative": str(negative),
                "priority": priority,
                "resolution": resolution,
                "video_duration": video_duration,
                "generate_audio": generate_audio,
                "upscale_scale": upscale_scale,
                "max_output": max_output,
                "source_image_urls": source_image_urls,
            },
        },
        {
            "id": output_id,
            "type": "image_output",
            "data": {"url": data.get("imageUrl") or data.get("url")},
        },
    ]

    flow_edges = [
        {
            "id": _new_id("edge"),
            "source": prompt_id,
            "sourceHandle": "output",
            "target": model_id,
            "targetHandle": "prompt_input",
        },
        {
            "id": _new_id("edge"),
            "source": model_id,
            "sourceHandle": "image_output",
            "target": output_id,
            "targetHandle": "input",
        },
    ]

    return {
        "nodes": flow_nodes,
        "edges": flow_edges,
        "_target_render_id": rid,
        "_execution_output_id": output_id,
    }


def graph_has_flow_nodes(graph: dict[str, Any]) -> bool:
    return any(n.get("type") in FLOW_TYPES for n in graph.get("nodes") or [])


def apply_output_to_render_node(
    canvas_graph: dict[str, Any],
    render_node_id: str,
    output_url: str | None,
    *,
    output_type: str = "image",
) -> dict[str, Any]:
    """Write generated media URL onto the visible render node."""
    graph = dict(canvas_graph)
    nodes = []
    is_video = output_type == "video"
    for n in graph.get("nodes") or []:
        node = dict(n)
        if node.get("id") == render_node_id and node.get("type") in CANVAS_RENDER_TYPES:
            data = dict(node.get("data") or {})
            if output_url:
                if is_video:
                    data["videoUrl"] = output_url
                    data.pop("imageUrl", None)
                else:
                    data["imageUrl"] = output_url
                    data.pop("videoUrl", None)
                data["url"] = output_url
                data["outputType"] = output_type
            data["status"] = "completed"
            node["data"] = data
        nodes.append(node)
    graph["nodes"] = nodes
    return graph
