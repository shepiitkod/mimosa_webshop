#!/usr/bin/env python3
"""Resize and save WebP + JPEG next to source assets in static/assets/images/."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "static" / "assets" / "images"
SOURCE_BASE = ROOT / "assets" / "images"

# (output stem, max width, max height, source filename)
JOBS: list[tuple[str, int | None, int | None, str]] = [
    ("photo1", 900, None, "photo1.ico"),
    ("photo2", 900, None, "photo2.ico"),
    ("photo3", 900, None, "photo3.ico"),
    *[(f"MAIN{i}", 800, None, f"MAIN{i}.ico") for i in range(1, 13)],
    ("bento", 600, None, "bento.ico"),
    ("contest-bouquet", 900, None, "contest-bouquet.png"),
    ("sv-hero-refill", 1100, None, "2026-06-10 14.40.35.ico"),
    ("mimosa-logo", 800, None, "logobl2.ico"),
]


def _open_any(path: Path) -> Image.Image:
    im = Image.open(path)
    if im.mode in ("RGBA", "P", "LA"):
        return im.convert("RGBA")
    return im.convert("RGB")


def _resize(im: Image.Image, max_w: int | None, max_h: int | None) -> Image.Image:
    w, h = im.size
    if max_w and w > max_w:
        ratio = max_w / w
        w, h = max_w, int(round(h * ratio))
    if max_h and h > max_h:
        ratio = max_h / h
        w, h = int(round(w * ratio)), max_h
    if (w, h) == im.size:
        return im
    return im.resize((w, h), Image.Resampling.LANCZOS)


def main() -> None:
    for stem, max_w, max_h, src_name in JOBS:
        src = BASE / src_name
        if not src.exists():
            src = SOURCE_BASE / src_name
        if not src.exists():
            print("skip (missing):", src)
            continue
        im = _open_any(src)
        im = _resize(im, max_w, max_h)
        webp = BASE / f"{stem}.webp"
        jpg = BASE / f"{stem}.jpg"
        if im.mode == "RGBA":
            background = Image.new("RGB", im.size, (255, 255, 255))
            background.paste(im, mask=im.split()[-1])
            im = background
        im.save(
            webp,
            "WEBP",
            quality=86,
            method=6,
        )
        im.save(
            jpg,
            "JPEG",
            quality=88,
            optimize=True,
            progressive=True,
        )
        print(
            f"{src_name} -> {webp.name} ({webp.stat().st_size // 1024} KB), "
            f"{jpg.name} ({jpg.stat().st_size // 1024} KB)"
        )


if __name__ == "__main__":
    main()
