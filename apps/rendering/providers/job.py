"""Normalized render request passed to provider adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RenderJob:
    prompt: str
    negative_prompt: str = ""
    model_slug: str = ""
    category_slug: str = ""
    model_name: str = ""
    output_type: str = "image"
    source_image_urls: list[str] = field(default_factory=list)
    settings: dict[str, Any] = field(default_factory=dict)

    def setting(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)
