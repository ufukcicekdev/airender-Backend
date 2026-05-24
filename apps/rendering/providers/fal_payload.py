"""Build Fal queue request bodies per model endpoint schema."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apps.core.media_urls import resolve_public_url_for_fal

if TYPE_CHECKING:
    from apps.catalog.models import AIModel

    from .endpoints import ModelEndpoint
    from .job import RenderJob


def _clean_prompt(prompt: str) -> str:
    """Remove internal canvas ref suffix from flow_builder."""
    text = (prompt or "").strip()
    if " [refs:" in text:
        text = text.split(" [refs:", 1)[0].strip()
    return text or "Create photorealistic image"


def _normalize_fal_resolution(value: str | None) -> str | None:
    """Fal expects '1K' | '2K' | '4K' (uppercase K); UI stores '1k' | '2k' | '4k'."""
    if not value:
        return None
    key = str(value).strip().lower()
    mapping = {"1k": "1K", "2k": "2K", "4k": "4K"}
    return mapping.get(key) or (str(value).strip() if str(value).strip() in ("1K", "2K", "4K") else None)


def _normalize_fal_aspect_ratio(value: str | None) -> str | None:
    if not value:
        return None
    v = str(value).strip().lower()
    if v in ("original", "auto", ""):
        return "auto"
    return str(value).strip()


def _resolved_source_urls(job: RenderJob) -> list[str]:
    urls: list[str] = []
    for raw in job.source_image_urls or []:
        resolved = resolve_public_url_for_fal(str(raw))
        if resolved:
            urls.append(resolved)
    return urls


def _path_lower(path: str) -> str:
    return (path or "").lower()


def _is_3d_job(job: RenderJob, endpoint: ModelEndpoint) -> bool:
    category = (job.category_slug or "").lower()
    if category == "3d-model" or endpoint.output_type == "model3d":
        return True
    path = _path_lower(endpoint.path)
    return "to-3d" in path or path.endswith("triposr")


def _is_multi_image_3d_path(path: str) -> bool:
    p = _path_lower(path)
    return "multi-image-to-3d" in p or "multiview-to-3d" in p


def _is_image_to_3d_path(path: str) -> bool:
    p = _path_lower(path)
    return "image-to-3d" in p or p.endswith("triposr")


def _is_text_to_3d_path(path: str) -> bool:
    return "text-to-3d" in _path_lower(path)


def _apply_3d_settings(body: dict[str, Any], job: RenderJob) -> None:
    topology = job.setting("topology")
    if topology:
        body["topology"] = topology

    polycount = job.setting("target_polycount")
    if polycount is not None:
        body["target_polycount"] = int(polycount)

    symmetry = job.setting("symmetry_mode")
    if symmetry:
        body["symmetry_mode"] = symmetry

    if job.setting("should_remesh") is not None:
        body["should_remesh"] = bool(job.setting("should_remesh"))
    if job.setting("should_texture") is not None:
        body["should_texture"] = bool(job.setting("should_texture"))


def build_fal_request_body(
    model: AIModel,
    job: RenderJob,
    endpoint: ModelEndpoint,
) -> dict[str, Any]:
    path = (endpoint.path or "").lower()
    category = (job.category_slug or "").lower()
    is_edit = "/edit" in path or category == "image-edit"
    is_video = endpoint.output_type == "video" or category == "image-to-video"
    is_3d = _is_3d_job(job, endpoint)

    body: dict[str, Any] = {
        "prompt": _clean_prompt(job.prompt),
    }

    neg = (job.negative_prompt or "").strip()
    if neg:
        body["negative_prompt"] = neg

    source_urls = _resolved_source_urls(job)

    if is_3d:
        endpoint_path = endpoint.path or ""
        if _is_multi_image_3d_path(endpoint_path):
            if "multiview" in _path_lower(endpoint_path):
                view_keys = [
                    "front_image_url",
                    "left_image_url",
                    "back_image_url",
                    "right_image_url",
                ]
                if not source_urls:
                    raise ValueError(
                        "Multiview 3D requires at least one reference image. "
                        "Connect a Source node on the canvas."
                    )
                for idx, url in enumerate(source_urls[:4]):
                    body[view_keys[idx]] = url
            else:
                if not source_urls:
                    raise ValueError(
                        "Multi-image 3D requires at least one reference image. "
                        "Connect a Source node on the canvas."
                    )
                body["image_urls"] = source_urls[:4]
        elif _is_image_to_3d_path(endpoint_path):
            if not source_urls:
                raise ValueError(
                    "This 3D model requires a reference image. "
                    "Connect a Source node on the canvas, then Make again."
                )
            body["image_url"] = source_urls[0]
            if len(source_urls) > 1:
                body["image_urls"] = source_urls[:4]
        elif _is_text_to_3d_path(endpoint_path):
            pass
        elif source_urls:
            body["image_url"] = source_urls[0]
        _apply_3d_settings(body, job)
    elif is_edit:
        if not source_urls:
            raise ValueError(
                "Image edit requires a source image. Connect a Source or a previous "
                "generation node to this render node, then save and try Make again."
            )
        body["image_urls"] = source_urls
    elif is_video:
        if not source_urls:
            raise ValueError("Video generation requires a source image URL.")
        body["image_url"] = source_urls[0]
    elif source_urls:
        body["image_urls"] = source_urls

    if not is_3d:
        resolution = _normalize_fal_resolution(job.setting("resolution"))
        if resolution:
            body["resolution"] = resolution

        aspect = _normalize_fal_aspect_ratio(job.setting("aspect_ratio"))
        if aspect:
            body["aspect_ratio"] = aspect

    if is_video:
        raw_duration = job.setting("video_duration") or job.setting("duration")
        if raw_duration:
            dur = str(raw_duration).strip()
            if dur.isdigit():
                dur = f"{dur}s"
            elif not dur.endswith("s"):
                dur = f"{dur}s"
            body["duration"] = dur
        if job.setting("generate_audio") is not None:
            body["generate_audio"] = bool(job.setting("generate_audio"))

    cfg = dict(model.config or {})
    for key in ("output_format", "num_images", "safety_tolerance"):
        if key in cfg and key not in body:
            body[key] = cfg[key]

    return body


def resolve_3d_endpoint_path(model: AIModel, source_count: int) -> str | None:
    """Pick image vs text vs multi-image Fal path from model config."""
    cfg = dict(model.config or {})
    base = str(cfg.get("endpoint_path") or "").strip()
    if source_count > 1 and cfg.get("multi_image_endpoint_path"):
        return str(cfg["multi_image_endpoint_path"])
    if source_count >= 1 and cfg.get("image_endpoint_path"):
        return str(cfg["image_endpoint_path"])
    if source_count >= 1 and base and _is_image_to_3d_path(base):
        return base
    if source_count >= 1 and base and not _is_text_to_3d_path(base):
        return base
    if source_count == 0 and cfg.get("text_endpoint_path"):
        return str(cfg["text_endpoint_path"])
    if source_count == 0 and base and _is_text_to_3d_path(base):
        return base
    return base or None
