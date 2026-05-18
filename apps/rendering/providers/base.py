from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from apps.catalog.models import AIModel

    from .job import RenderJob

ProgressCallback = Callable[[int, str], None]


class ProviderAdapter(ABC):
    """Single backend (Comfy, direct API, etc.)."""

    @abstractmethod
    def run(
        self,
        model: AIModel,
        job: RenderJob,
        *,
        on_progress: ProgressCallback | None = None,
    ) -> str:
        """Return output image URL (https or data:image/...)."""
