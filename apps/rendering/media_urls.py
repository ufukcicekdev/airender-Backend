"""Helpers for classifying render output URLs."""

from __future__ import annotations

_VIDEO_SUFFIXES = (".mp4", ".webm", ".mov", ".m4v")
_MODEL3D_SUFFIXES = (".glb", ".gltf", ".obj", ".fbx")
_IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".gif")


def _path_lower(url: str) -> str:
    return url.split("?")[0].lower()


def looks_like_video_url(url: str | None) -> bool:
    if not url:
        return False
    path = _path_lower(url)
    return any(path.endswith(suffix) for suffix in _VIDEO_SUFFIXES)


def looks_like_model3d_url(url: str | None) -> bool:
    if not url:
        return False
    if url.startswith("data:model/gltf-binary"):
        return True
    path = _path_lower(url)
    return any(path.endswith(suffix) for suffix in _MODEL3D_SUFFIXES)


def looks_like_image_url(url: str | None) -> bool:
    if not url:
        return False
    if url.startswith("data:image/"):
        return True
    path = _path_lower(url)
    return any(path.endswith(suffix) for suffix in _IMAGE_SUFFIXES)


def is_model3d_mesh_url(url: str | None) -> bool:
    """True when URL points at an actual mesh file (GLB/GLTF), not a raster preview."""
    if not url:
        return False
    if url.startswith("data:model/gltf-binary"):
        return True
    path = _path_lower(url)
    return path.endswith(".glb") or path.endswith(".gltf")
