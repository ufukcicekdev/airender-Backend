"""Google AI (Imagen / Gemini) — direct API, no Fal."""

from __future__ import annotations

import base64
import json
import logging
from typing import TYPE_CHECKING
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .base import ProgressCallback, ProviderAdapter
from .endpoints import resolve_model_endpoint
from .stub import StubAdapter

if TYPE_CHECKING:
    from apps.catalog.models import AIModel

    from .job import RenderJob

logger = logging.getLogger(__name__)

IMAGEN_PREDICT_PATH = "models/imagen-3.0-generate-002:predict"


class GoogleAdapter(ProviderAdapter):
    def __init__(self) -> None:
        self._stub = StubAdapter()

    def run(
        self,
        model: AIModel,
        job: RenderJob,
        *,
        on_progress: ProgressCallback | None = None,
    ) -> str:
        endpoint = resolve_model_endpoint(model)
        api_key = (endpoint.api_key or "").strip()
        base_url = (endpoint.base_url or "").strip().rstrip("/")

        if not api_key or not base_url:
            logger.info("Google AI key missing for %s — stub", model.slug)
            return self._stub.run(model, job, on_progress=on_progress)

        if on_progress:
            on_progress(15, "google_request")

        path = (endpoint.path or IMAGEN_PREDICT_PATH).lstrip("/")
        if "generateContent" in path and job.category_slug != "image-to-video":
            return self._gemini_text_only(model, job, base_url, path, api_key, on_progress)

        if job.source_image_urls and job.category_slug == "image-edit":
            logger.warning(
                "Google image-edit (%s) needs Imagen edit API — using stub for now",
                model.slug,
            )
            return self._stub.run(model, job, on_progress=on_progress)

        try:
            url = f"{base_url}/{path}?key={api_key}"
            body = {
                "instances": [{"prompt": job.prompt or "photorealistic image"}],
                "parameters": {"sampleCount": 1},
            }
            req = Request(
                url,
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode())

            predictions = data.get("predictions") or []
            if predictions:
                pred = predictions[0]
                b64 = pred.get("bytesBase64Encoded") or pred.get("bytesBase64")
                mime = pred.get("mimeType") or "image/png"
                if b64:
                    if on_progress:
                        on_progress(95, "google_done")
                    return f"data:{mime};base64,{b64}"

            logger.warning("Google Imagen empty response for %s: %s", model.slug, data)
        except HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode()[:500]
            except OSError:
                pass
            logger.error(
                "Google API HTTP %s for %s: %s",
                exc.code,
                model.slug,
                body,
            )
        except (URLError, json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.exception("Google adapter failed for %s: %s", model.slug, exc)

        return self._stub.run(model, job, on_progress=on_progress)

    def _gemini_text_only(
        self,
        model: AIModel,
        job: RenderJob,
        base_url: str,
        path: str,
        api_key: str,
        on_progress: ProgressCallback | None,
    ) -> str:
        """Gemini generateContent returns text, not images — stub for image workflows."""
        logger.warning(
            "Model %s uses Gemini text endpoint; use Imagen predict path for images",
            model.slug,
        )
        return self._stub.run(model, job, on_progress=on_progress)
