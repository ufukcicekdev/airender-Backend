import io

from PIL import Image


def generate_thumbnail(image_field, max_size: int = 256) -> io.BytesIO | None:
    try:
        img = Image.open(image_field)
        img.thumbnail((max_size, max_size))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        return buffer
    except Exception:
        return None


def get_image_dimensions(image_field) -> tuple[int, int]:
    try:
        img = Image.open(image_field)
        return img.size
    except Exception:
        return 0, 0
