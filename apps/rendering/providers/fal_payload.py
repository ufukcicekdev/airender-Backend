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


def build_fal_request_body(
    model: AIModel,
    job: RenderJob,
    endpoint: ModelEndpoint,
) -> dict[str, Any]:
    path = (endpoint.path or "").lower()
    category = (job.category_slug or "").lower()
    is_edit = "/edit" in path or category == "image-edit"
    is_video = endpoint.output_type == "video" or category == "image-to-video"

    body: dict[str, Any] = {
        "prompt": _clean_prompt(job.prompt),
    }

    neg = (job.negative_prompt or "").strip()
    if neg:
        body["negative_prompt"] = neg

    source_urls = _resolved_source_urls(job)

    if is_edit:
        if not source_urls:
            raise ValueError(
                "Image edit requires a source image. Upload a Source on the canvas "
                "and connect it to the generation node."
            )
        body["image_urls"] = source_urls
    elif is_video:
        if not source_urls:
            raise ValueError("Video generation requires a source image URL.")
        body["image_url"] = source_urls[0]
    elif source_urls:
        # Reference-guided generation (some t2i models accept image_urls)
        body["image_urls"] = source_urls

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
