from __future__ import annotations

import os
from pathlib import Path

from django.conf import settings

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

PRODUCT_IMAGE_WIDTHS = (400, 800, 1200)


def _open_image(path: Path):
    if Image is None or not path.exists():
        return None
    try:
        return Image.open(path)
    except OSError:
        return None


def generate_product_image_variants(image_field) -> None:
    """Create WebP width variants beside the uploaded product image."""
    if not image_field or Image is None:
        return

    source_path = Path(image_field.path)
    if not source_path.exists():
        return

    image = _open_image(source_path)
    if image is None:
        return

    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA" if "A" in image.getbands() else "RGB")

    stem = source_path.stem
    parent = source_path.parent

    for width in PRODUCT_IMAGE_WIDTHS:
        if image.width <= width:
            continue
        ratio = width / float(image.width)
        height = max(1, int(image.height * ratio))
        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        target = parent / f"{stem}_{width}.webp"
        resized.save(target, format="WEBP", quality=88, method=6)


def product_variant_url(image_field, width: int) -> str | None:
    if not image_field:
        return None
    source_path = Path(image_field.path)
    variant = source_path.parent / f"{source_path.stem}_{width}.webp"
    if not variant.exists():
        return None
    media_root = Path(settings.MEDIA_ROOT).resolve()
    return variant.resolve().relative_to(media_root).as_posix()
