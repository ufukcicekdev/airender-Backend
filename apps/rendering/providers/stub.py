"""Development fallback when no GPU / provider is configured."""

from __future__ import annotations

import base64
import io
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw

from .base import ProgressCallback, ProviderAdapter

if TYPE_CHECKING:
    from apps.catalog.models import AIModel

    from .job import RenderJob


class StubAdapter(ProviderAdapter):
    def run(
        self,
        model: AIModel,
        job: RenderJob,
        *,
        on_progress: ProgressCallback | None = None,
    ) -> str:
        if on_progress:
            on_progress(40, "stub_render")
            on_progress(85, "stub_encode")

        w, h = 512, 512
        ratio = str(job.setting("aspect_ratio", "1:1"))
        if ratio == "16:9":
            w, h = 640, 360
        elif ratio == "9:16":
            w, h = 360, 640

        img = Image.new("RGB", (w, h), color=(22, 24, 32))
        draw = ImageDraw.Draw(img)
        draw.rectangle([24, 24, w - 24, h - 24], outline=(45, 212, 191), width=2)
        draw.text((36, 36), model.name[:32], fill=(148, 163, 184))
        draw.text((36, 56), (job.prompt or "")[:72], fill=(100, 116, 139))
        provider_label = model.provider or "local"
        kind = getattr(job, "output_type", "image") or "image"
        draw.text((36, h - 36), f"{provider_label} · {kind} · stub", fill=(80, 90, 110))

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/png;base64,{b64}"
