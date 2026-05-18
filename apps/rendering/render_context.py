"""Build render context from canvas graph + resolve credit cost."""

from __future__ import annotations

from typing import Any

from apps.rendering.providers import resolve_ai_model


def get_render_node(
    graph: dict[str, Any], render_node_id: str | None
) -> tuple[dict | None, dict[str, dict]]:
    nodes = graph.get("nodes") or []
    node_by_id = {n["id"]: n for n in nodes if n.get("id")}
    if render_node_id and render_node_id in node_by_id:
        node = node_by_id[render_node_id]
        if node.get("type") in ("render", "detail"):
            return node, node_by_id
    for n in nodes:
        if n.get("type") in ("render", "detail"):
            return n, node_by_id
    return None, node_by_id


def credit_cost_for_render(graph: dict[str, Any], render_node_id: str | None) -> int:
    node, _ = get_render_node(graph, render_node_id)
    if not node:
        return 1
    data = node.get("data") or {}
    model = resolve_ai_model(
        str(data.get("categorySlug") or ""),
        str(data.get("modelSlug") or ""),
    )
    if model:
        return max(1, model.credit_cost)
    return 1


def source_urls_for_render(
    graph: dict[str, Any],
    render_node_id: str | None,
    node_by_id: dict[str, dict],
) -> list[str]:
    node, _ = get_render_node(graph, render_node_id)
    if not node:
        return []
    rid = node["id"]
    edges = graph.get("edges") or []
    urls: list[str] = []
    for e in edges:
        if e.get("target") != rid:
            continue
        src = node_by_id.get(e.get("source", ""))
        if not src or src.get("type") != "source":
            continue
        url = (src.get("data") or {}).get("imageUrl")
        if url and isinstance(url, str):
            urls.append(url)
    return urls


CATEGORIES_REQUIRING_SOURCE = frozenset(
    {"image-to-video", "upscale", "image-edit"}
)


def count_render_input_images(
    graph: dict[str, Any], render_node_id: str | None
) -> int:
    node, node_by_id = get_render_node(graph, render_node_id)
    if not node:
        return 0
    urls = source_urls_for_render(graph, render_node_id, node_by_id)
    if urls:
        return len(urls)
    data = node.get("data") or {}
    stored = data.get("inputImages") or []
    return sum(
        1
        for item in stored
        if isinstance(item, dict) and item.get("url")
    )


def validate_render_inputs(
    graph: dict[str, Any], render_node_id: str | None
) -> str | None:
    """Return user-facing error message, or None if inputs are sufficient."""
    node, _ = get_render_node(graph, render_node_id)
    if not node:
        return "No render node found in workflow."

    data = node.get("data") or {}
    category_slug = str(data.get("categorySlug") or "")
    model_slug = str(data.get("modelSlug") or "")
    model = resolve_ai_model(category_slug, model_slug)

    requires_images = False
    min_images = 0

    if model:
        requires_images = bool(model.requires_images)
        min_images = int(model.min_input_images or 0)
    elif category_slug in CATEGORIES_REQUIRING_SOURCE:
        requires_images = True
        min_images = 1

    if category_slug in CATEGORIES_REQUIRING_SOURCE:
        requires_images = True
        if min_images < 1:
            min_images = 1

    if requires_images and min_images < 1:
        min_images = 1

    if not requires_images and min_images < 1:
        return None

    count = count_render_input_images(graph, render_node_id)
    if requires_images and count < 1:
        return (
            "At least one source image is required for this model. "
            "Upload a Source image on the canvas and connect it before Make."
        )
    if count < min_images:
        return (
            f"This model requires at least {min_images} input image(s). "
            f"Currently connected: {count}."
        )
    return None
