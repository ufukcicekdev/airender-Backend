import io
import logging
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

_VIDEO_URL_SUFFIXES = (".mp4", ".webm", ".mov", ".m4v")

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image

from apps.core.media_urls import public_media_url
from apps.projects.activity import record_project_activity
from apps.rendering.models import GeneratedImage, RenderTask, RenderTaskStatus
from apps.rendering.render_context import get_render_node
from apps.workflow.flow_builder import (
    apply_output_to_render_node,
    build_execution_flow_from_canvas,
    graph_has_flow_nodes,
)
from apps.workflow.graph_engine import GraphExecutionError, execute_flow_graph


def _absolute_media_url(url: str) -> str:
    if url.startswith("data:"):
        return url
    if url.startswith(("http://", "https://")):
        return url
    if getattr(settings, "USE_S3", False):
        base = settings.MEDIA_URL.rstrip("/")
        path = url.lstrip("/")
        if path.startswith("media/"):
            path = path[6:]
        return f"{base}/{path.lstrip('/')}"
    if "/media/" in url:
        return url[url.find("/media/") :]
    base = settings.BACKEND_PUBLIC_URL.rstrip("/")
    if url.startswith("/"):
        return f"{base}{url}"
    return f"{base}/{url}"


def _looks_like_video_url(url: str | None) -> bool:
    if not url:
        return False
    path = url.split("?")[0].lower()
    return any(path.endswith(suffix) for suffix in _VIDEO_URL_SUFFIXES)


def _output_type_for_task(task: RenderTask, output_url: str | None = None) -> str:
    graph = task.workflow.graph or {}
    rid = (task.node_statuses or {}).get("_target_render_id") or None
    node, _ = get_render_node(graph, rid)
    if not node:
        return "video" if _looks_like_video_url(output_url) else "image"
    data = node.get("data") or {}
    if data.get("categorySlug") == "image-to-video":
        return "video"
    if str(data.get("outputType") or "").lower() == "video":
        return "video"
    if data.get("videoUrl") and not data.get("imageUrl"):
        return "video"
    if _looks_like_video_url(output_url):
        return "video"
    return str(data.get("outputType") or "image")


def _fetch_remote_bytes(url: str, *, timeout: int = 120) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": "Flowframe/1.0 (+https://flowframe.app)",
            "Accept": "*/*",
        },
    )
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _extract_task_output(task: RenderTask) -> tuple[str | None, str]:
    gen = task.images.order_by("-created_at").first()
    gen_url = _absolute_media_url(gen.image.url) if gen and gen.image else None
    output_type = _output_type_for_task(task, gen_url)
    if gen and gen.image:
        meta = gen.metadata or {}
        declared = str(meta.get("output_type") or output_type)
        if declared != "video" and _looks_like_video_url(gen_url):
            declared = "video"
        return gen_url, declared

    graph = task.workflow.graph or {}
    rid = (task.node_statuses or {}).get("_target_render_id") or None
    node, _ = get_render_node(graph, rid)
    if not node:
        return None, output_type
    data = node.get("data") or {}
    if data.get("videoUrl"):
        return str(data["videoUrl"]), "video"
    if data.get("imageUrl"):
        return str(data["imageUrl"]), str(data.get("outputType") or "image")
    return None, output_type


def broadcast_render_update(task_id: str, payload: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"render_{task_id}",
        {"type": "render.update", "payload": payload},
    )


def _ws_payload(task: RenderTask) -> dict:
    output_url, output_type = _extract_task_output(task)
    payload = {
        "task_id": str(task.id),
        "status": task.status,
        "progress": task.progress,
        "current_stage": task.current_stage,
        "node_statuses": task.node_statuses,
        "error_message": task.error_message,
        "flow_data": task.workflow.graph,
        "output_type": output_type,
    }
    if output_url:
        payload["output_url"] = output_url
    return payload


def update_task(task: RenderTask, **kwargs):
    new_status = kwargs.get("status")
    for key, value in kwargs.items():
        setattr(task, key, value)
    task.save()
    if new_status == RenderTaskStatus.COMPLETED:
        output_type = _output_type_for_task(task)
        summary = (
            "Video generated" if output_type == "video" else "Generation completed"
        )
        record_project_activity(task.workflow.project_id, summary)
    elif new_status == RenderTaskStatus.FAILED:
        record_project_activity(task.workflow.project_id, "Generation failed")
    broadcast_render_update(str(task.id), _ws_payload(task))


@shared_task(bind=True, name="apps.rendering.tasks.run_render_pipeline")
def run_render_pipeline(self, task_id: str):
    try:
        task = RenderTask.objects.select_related("workflow", "user").get(id=task_id)
    except RenderTask.DoesNotExist:
        return

    if task.status == RenderTaskStatus.CANCELLED:
        return

    canvas_graph = dict(task.workflow.graph or {})
    target_render_id = (task.node_statuses or {}).get("_target_render_id") or None

    built = (
        None
        if graph_has_flow_nodes(canvas_graph)
        else build_execution_flow_from_canvas(canvas_graph, target_render_id)
    )
    if built:
        target_render_id = built.get("_target_render_id") or target_render_id

    nodes = (built or canvas_graph).get("nodes", [])
    has_flow_nodes = bool(built) or graph_has_flow_nodes(canvas_graph)

    statuses = {n.get("id", ""): "queued" for n in nodes}
    if target_render_id:
        statuses[target_render_id] = "queued"

    update_task(
        task,
        status=RenderTaskStatus.PROCESSING,
        started_at=timezone.now(),
        celery_task_id=self.request.id or "",
        current_stage="graph_parse",
        progress=5,
        node_statuses=statuses,
    )

    task.refresh_from_db()
    if task.status == RenderTaskStatus.CANCELLED:
        return

    if has_flow_nodes:
        try:
            update_task(task, current_stage="dag_execute", progress=15)
            if built:
                output_node_id = built.get("_execution_output_id")
                exec_graph = {"nodes": built["nodes"], "edges": built["edges"]}
            else:
                output_node_id = None
                exec_graph = canvas_graph

            def on_provider_progress(pct: int, stage: str) -> None:
                task.refresh_from_db()
                if task.status == RenderTaskStatus.CANCELLED:
                    return
                mapped = 15 + int(pct * 0.75)
                update_task(
                    task,
                    current_stage=stage,
                    progress=min(95, mapped),
                )

            updated_flow, node_statuses = execute_flow_graph(
                exec_graph, on_progress=on_provider_progress
            )

            output_url = None
            if output_node_id:
                for node in updated_flow.get("nodes", []):
                    if node.get("id") == output_node_id:
                        output_url = node.get("data", {}).get("url")
                        break
            if not output_url:
                for node in updated_flow.get("nodes", []):
                    if node.get("type") == "image_output":
                        output_url = node.get("data", {}).get("url")
                        break

            output_type = _output_type_for_task(task, output_url)
            display_url = _persist_provider_output(
                task, output_url, output_type=output_type
            )

            if target_render_id and display_url:
                canvas_graph = apply_output_to_render_node(
                    canvas_graph,
                    target_render_id,
                    display_url,
                    output_type=output_type,
                )
                task.workflow.graph = canvas_graph
                task.workflow.save(update_fields=["graph", "updated_at"])
                node_statuses[target_render_id] = "completed"

            update_task(
                task,
                status=RenderTaskStatus.COMPLETED,
                progress=100,
                current_stage="done",
                completed_at=timezone.now(),
                node_statuses=node_statuses,
            )
            return
        except GraphExecutionError as exc:
            update_task(
                task,
                status=RenderTaskStatus.FAILED,
                error_message=str(exc),
                completed_at=timezone.now(),
            )
            return

    _run_legacy_linear_pipeline(self, task)


def _run_legacy_linear_pipeline(celery_task, task: RenderTask):
    """Fallback for older canvas node types (source/render)."""
    from PIL import ImageDraw

    stages = [
        ("preprocessing", 20),
        ("rendering", 55),
        ("enhancement", 80),
        ("export", 95),
    ]

    node_statuses = dict(task.node_statuses)
    graph = task.workflow.graph or {}
    nodes = graph.get("nodes", [])

    for node in nodes:
        node_statuses[node.get("id", "")] = "queued"

    for stage_name, progress in stages:
        task.refresh_from_db()
        if task.status == RenderTaskStatus.CANCELLED:
            return

        update_task(task, current_stage=stage_name, progress=progress)

        for node in nodes:
            nid = node.get("id", "")
            node_statuses[nid] = "processing"
            update_task(task, node_statuses=node_statuses)
            time.sleep(0.4)
            node_statuses[nid] = "completed"
            update_task(task, node_statuses=node_statuses)

    _save_placeholder_image(task, label="Flowframe Render")

    update_task(
        task,
        status=RenderTaskStatus.COMPLETED,
        progress=100,
        current_stage="done",
        completed_at=timezone.now(),
        node_statuses=node_statuses,
    )


def _persist_provider_output(
    task: RenderTask,
    output_url: str | None,
    *,
    output_type: str = "image",
) -> str | None:
    """
    Download Fal/provider output into default storage (S3/Spaces when USE_S3=1).
    Returns a public URL for the canvas — never a temporary Fal CDN URL.
    """
    if not output_url:
        _save_placeholder_image(task, label="No output")
        return _latest_persisted_url(task)

    resolved_type = output_type
    if resolved_type != "video" and _looks_like_video_url(output_url):
        resolved_type = "video"

    if output_url.startswith("data:image"):
        _save_data_url_image(task, output_url, output_type=resolved_type)
    elif resolved_type == "video" and output_url.startswith(("http://", "https://")):
        saved = _save_remote_video(task, output_url, output_type=resolved_type)
        if not saved:
            raise ValueError(
                "Video could not be saved from the provider. Try Make again in a moment."
            )
    elif output_url.startswith(("http://", "https://")):
        _save_remote_image(task, output_url, output_type=resolved_type)
    else:
        _save_placeholder_image(task, label="Flow output")
        return _latest_persisted_url(task)

    return _latest_persisted_url(task)


def _latest_persisted_url(task: RenderTask) -> str | None:
    gen = task.images.order_by("-created_at").first()
    if gen and gen.image:
        return public_media_url(gen.image)
    return None


def _save_remote_image(
    task: RenderTask, url: str, *, output_type: str = "image"
) -> None:
    if _looks_like_video_url(url):
        saved = _save_remote_video(task, url, output_type="video")
        if saved:
            return
        raise ValueError("Video download failed")
    try:
        raw = _fetch_remote_bytes(url, timeout=90)
        buffer = io.BytesIO(raw)
        img = Image.open(buffer)
        _persist_image(task, img, output_type=output_type)
    except (URLError, OSError, ValueError):
        logger.exception("Image download failed for task %s: %s", task.id, url)
        _save_placeholder_image(task, label="Download failed")


def _save_remote_video(
    task: RenderTask, url: str, *, output_type: str = "video"
) -> bool:
    try:
        raw = _fetch_remote_bytes(url, timeout=180)
        if len(raw) < 256:
            raise ValueError("Video payload too small")
        gen = GeneratedImage(
            render_task=task,
            width=0,
            height=0,
            metadata={"output_type": output_type, "source_url": url},
        )
        gen.image.save(
            f"{task.id}.mp4",
            ContentFile(raw),
            save=True,
        )
        gen.save()
        return True
    except (URLError, OSError, ValueError) as exc:
        logger.exception("Video download failed for task %s: %s", task.id, url)
        return False


def _save_data_url_image(task: RenderTask, data_url: str, *, output_type: str = "image"):
    import base64

    header, encoded = data_url.split(",", 1)
    raw = base64.b64decode(encoded)
    buffer = io.BytesIO(raw)
    img = Image.open(buffer)
    _persist_image(task, img, output_type=output_type)


def _save_placeholder_image(task: RenderTask, label: str = "Flowframe"):
    from PIL import ImageDraw

    img = Image.new("RGB", (512, 512), color=(18, 18, 24))
    draw = ImageDraw.Draw(img)
    draw.rectangle([64, 64, 448, 448], outline=(99, 102, 241), width=3)
    draw.text((180, 240), label, fill=(148, 163, 184))
    _persist_image(task, img)


def _persist_image(
    task: RenderTask, img: Image.Image, *, output_type: str = "image"
):
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    gen = GeneratedImage(
        render_task=task,
        width=img.width,
        height=img.height,
        metadata={"output_type": output_type},
    )
    gen.image.save(f"{task.id}.png", ContentFile(buffer.read()), save=True)

    thumb = img.copy()
    thumb.thumbnail((256, 256))
    tb = io.BytesIO()
    thumb.save(tb, format="PNG")
    tb.seek(0)
    gen.thumbnail.save(f"{task.id}_thumb.png", ContentFile(tb.read()), save=True)
    gen.save()
