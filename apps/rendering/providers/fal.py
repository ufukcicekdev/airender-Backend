"""Fal.ai queue API adapter (optional — set FAL_API_KEY in .env)."""

from __future__ import annotations

import json
import logging
import time
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


class FalAdapter(ProviderAdapter):
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
        if not endpoint.api_key or not endpoint.path:
            logger.info("Fal not configured for %s — stub", model.slug)
            return self._stub.run(model, job, on_progress=on_progress)

        if on_progress:
            on_progress(15, "fal_queue")

        try:
            body: dict = {
                "prompt": job.prompt,
                "negative_prompt": job.negative_prompt or "",
            }
            if job.source_image_urls:
                body["image_url"] = job.source_image_urls[0]

            req = Request(
                endpoint.submit_url,
                data=json.dumps(body).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Key {endpoint.api_key}",
                },
                method="POST",
            )
            with urlopen(req, timeout=60) as resp:
                queued = json.loads(resp.read().decode())

            status_url = queued.get("status_url") or queued.get("response_url")
            if not status_url:
                raise ValueError("Fal response missing status_url")

            poll = float((endpoint.extra or {}).get("poll_interval_sec", 2))
            timeout = int((endpoint.extra or {}).get("timeout_sec", 300))
            deadline = time.time() + timeout
            last_pct = 30

            while time.time() < deadline:
                status_req = Request(
                    status_url,
                    headers={"Authorization": f"Key {endpoint.api_key}"},
                )
                with urlopen(status_req, timeout=30) as resp:
                    status_data = json.loads(resp.read().decode())

                state = str(status_data.get("status", "")).upper()
                if state in ("COMPLETED", "OK", "SUCCESS"):
                    if on_progress:
                        on_progress(90, "fal_download")
                    return self._extract_output(status_data, endpoint)

                if state in ("FAILED", "ERROR"):
                    raise ValueError(status_data.get("error") or "Fal job failed")

                if on_progress and last_pct < 85:
                    last_pct = min(85, last_pct + 5)
                    on_progress(last_pct, "fal_processing")
                time.sleep(poll)

            raise TimeoutError("Fal job timed out")
        except (URLError, HTTPError, TimeoutError, ValueError, KeyError) as exc:
            logger.exception("Fal adapter failed for %s: %s", model.slug, exc)
            return self._stub.run(model, job, on_progress=on_progress)

    def _extract_output(self, status_data: dict, endpoint) -> str:
        response_url = status_data.get("response_url")
        if response_url:
            req = Request(
                response_url,
                headers={"Authorization": f"Key {endpoint.api_key}"},
            )
            with urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
        else:
            result = status_data

        if endpoint.output_type == "video":
            videos = result.get("video") or result.get("videos") or []
            if isinstance(videos, dict):
                url = videos.get("url")
                if url:
                    return str(url)
            if isinstance(videos, list) and videos:
                item = videos[0]
                if isinstance(item, str):
                    return item
                if isinstance(item, dict) and item.get("url"):
                    return str(item["url"])

        images = result.get("images") or result.get("image") or []
        if isinstance(images, dict) and images.get("url"):
            return str(images["url"])
        if isinstance(images, list) and images:
            item = images[0]
            if isinstance(item, str):
                return item
            if isinstance(item, dict) and item.get("url"):
                return str(item["url"])

        url = result.get("url")
        if url:
            return str(url)
        raise ValueError("Fal response has no output URL")
