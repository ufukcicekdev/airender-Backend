"""ComfyUI provider — submits workflows to a self-hosted Comfy instance."""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import TYPE_CHECKING
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings

from .base import ProgressCallback, ProviderAdapter
from .stub import StubAdapter

if TYPE_CHECKING:
    from apps.catalog.models import AIModel

    from .job import RenderJob

logger = logging.getLogger(__name__)


class ComfyAdapter(ProviderAdapter):
    """
    Calls ComfyUI HTTP API when COMFYUI_URL is set and reachable.
    Falls back to StubAdapter if Comfy is down or workflow is missing.
    """

    def __init__(self) -> None:
        self._stub = StubAdapter()

    def run(
        self,
        model: AIModel,
        job: RenderJob,
        *,
        on_progress: ProgressCallback | None = None,
    ) -> str:
        base_url = (getattr(settings, "COMFYUI_URL", None) or "").rstrip("/")
        if not base_url:
            logger.info("COMFYUI_URL not set — using stub for %s", model.slug)
            return self._stub.run(model, job, on_progress=on_progress)

        if on_progress:
            on_progress(10, "comfy_connect")

        if not self._ping(base_url):
            logger.warning("ComfyUI unreachable at %s — stub fallback", base_url)
            return self._stub.run(model, job, on_progress=on_progress)

        workflow = self._build_workflow(model, job)
        if not workflow:
            return self._stub.run(model, job, on_progress=on_progress)

        if on_progress:
            on_progress(25, "comfy_queue")

        try:
            prompt_id = self._queue_prompt(base_url, workflow)
            if on_progress:
                on_progress(50, "comfy_processing")
            image_ref = self._wait_for_output(
                base_url, prompt_id, on_progress=on_progress
            )
            if image_ref:
                url = self._resolve_image_url(base_url, image_ref)
                if url and on_progress:
                    on_progress(95, "comfy_done")
                return url or self._stub.run(model, job, on_progress=on_progress)
        except (URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            logger.exception("ComfyUI job failed: %s", exc)

        return self._stub.run(model, job, on_progress=on_progress)

    def _ping(self, base_url: str) -> bool:
        try:
            with urlopen(f"{base_url}/system_stats", timeout=5) as resp:
                return resp.status == 200
        except URLError:
            return False

    def _queue_prompt(self, base_url: str, workflow: dict) -> str:
        client_id = str(uuid.uuid4())
        body = json.dumps({"prompt": workflow, "client_id": client_id}).encode()
        req = Request(
            f"{base_url}/prompt",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        return str(data["prompt_id"])

    def _wait_for_output(
        self,
        base_url: str,
        prompt_id: str,
        *,
        on_progress: ProgressCallback | None = None,
        timeout_sec: int = 300,
        poll_interval: float = 1.5,
    ) -> dict | None:
        deadline = time.time() + timeout_sec
        last_progress = 50
        while time.time() < deadline:
            history = self._get_history(base_url, prompt_id)
            if history and prompt_id in history:
                outputs = history[prompt_id].get("outputs") or {}
                for node_out in outputs.values():
                    images = node_out.get("images") or []
                    if images:
                        return images[0]
            if on_progress and last_progress < 90:
                last_progress = min(90, last_progress + 5)
                on_progress(last_progress, "comfy_processing")
            time.sleep(poll_interval)
        return None

    def _get_history(self, base_url: str, prompt_id: str) -> dict:
        with urlopen(f"{base_url}/history/{prompt_id}", timeout=15) as resp:
            return json.loads(resp.read().decode())

    def _resolve_image_url(self, base_url: str, image_ref: dict) -> str | None:
        filename = image_ref.get("filename")
        subfolder = image_ref.get("subfolder") or ""
        img_type = image_ref.get("type") or "output"
        if not filename:
            return None
        qs = urlencode(
            {"filename": filename, "subfolder": subfolder, "type": img_type}
        )
        return f"{base_url}/view?{qs}"

    def _build_workflow(self, model: AIModel, job: RenderJob) -> dict | None:
        """
        Minimal text-to-image workflow for ComfyUI.
        Replace with workflow JSON keyed by model.external_id in production.
        """
        prompt = job.prompt or "high quality image"
        negative = job.negative_prompt or "blurry, low quality"
        seed = abs(hash(f"{job.model_slug}-{prompt}")) % (2**31)

        return {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": 20,
                    "cfg": 7.5,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                },
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"},
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 512, "height": 512, "batch_size": 1},
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["4", 1]},
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": negative, "clip": ["4", 1]},
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": f"vizmake_{model.slug}",
                    "images": ["8", 0],
                },
            },
        }
