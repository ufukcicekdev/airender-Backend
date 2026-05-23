"""
HTTP adapters for direct provider APIs (Replicate, OpenAI, Magnific, Runway, …).

When API key + endpoint are configured, attempts a minimal POST.
Otherwise falls back to stub so the UI flow still works in dev.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING
from urllib.error import URLError
from urllib.request import Request, urlopen

from .base import ProgressCallback, ProviderAdapter
from .endpoints import resolve_model_endpoint
from .stub import StubAdapter

if TYPE_CHECKING:
    from apps.catalog.models import AIModel

    from .job import RenderJob

logger = logging.getLogger(__name__)


class ExternalHttpAdapter(ProviderAdapter):
    """Generic direct-API adapter driven by ModelEndpoint + AIModel.config."""

    def __init__(self, provider_key: str) -> None:
        self.provider_key = provider_key
        self._stub = StubAdapter()

    def run(
        self,
        model: AIModel,
        job: RenderJob,
        *,
        on_progress: ProgressCallback | None = None,
    ) -> str:
        endpoint = resolve_model_endpoint(model)
        if not endpoint.api_key or not endpoint.base_url:
            logger.info(
                "%s not configured for %s — stub",
                self.provider_key,
                model.slug,
            )
            return self._stub.run(model, job, on_progress=on_progress)

        if on_progress:
            on_progress(20, f"{self.provider_key}_request")

        try:
            body = {
                "prompt": job.prompt,
                "negative_prompt": job.negative_prompt,
                "model": model.external_id or model.slug,
                "image_url": job.source_image_urls[0]
                if job.source_image_urls
                else None,
                **(model.config or {}),
            }
            body = {k: v for k, v in body.items() if v is not None and k != "endpoint_path"}

            url = endpoint.submit_url
            headers = {"Content-Type": "application/json"}
            if endpoint.provider == "google":
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}key={endpoint.api_key}"
            else:
                headers["Authorization"] = f"Bearer {endpoint.api_key}"

            req = Request(
                url,
                data=json.dumps(body).encode(),
                headers=headers,
                method=endpoint.submit_method,
            )
            with urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())

            url = (
                data.get("output_url")
                or data.get("url")
                or (data.get("output") or {}).get("url")
            )
            if url:
                if on_progress:
                    on_progress(95, f"{self.provider_key}_done")
                return str(url)
        except (URLError, json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.exception("%s adapter failed: %s", self.provider_key, exc)

        return self._stub.run(model, job, on_progress=on_progress)
