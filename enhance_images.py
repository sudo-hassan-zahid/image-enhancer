#!/usr/bin/env python3
"""Convert images from ./images to optimized WEBP files."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def iter_images(source_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in source_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def enhance_image(
    image: Image.Image,
    contrast: float,
    color: float,
    sharpness: float,
) -> Image.Image:
    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image = ImageEnhance.Color(image).enhance(color)
    image = ImageEnhance.Sharpness(image).enhance(sharpness)
    return image.filter(ImageFilter.UnsharpMask(radius=1.4, percent=135, threshold=3))


def convert_image(
    input_path: Path,
    output_dir: Path,
    quality: int,
    contrast: float,
    color: float,
    sharpness: float,
) -> Path:
    output_path = output_dir / f"{input_path.stem}.webp"

    with Image.open(input_path) as image:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        image = enhance_image(image, contrast, color, sharpness)
        image.save(output_path, "WEBP", quality=quality, method=6, optimize=True)

    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert images from ./images to lightweight WEBP assets."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("images"),
        help="Folder containing source images. Defaults to ./images.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/images"),
        help="Folder for generated WEBP images. Defaults to ./dist/images.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=82,
        choices=range(1, 101),
        metavar="1-100",
        help="WEBP quality level. Defaults to 82.",
    )
    parser.add_argument(
        "--contrast",
        type=float,
        default=1.08,
        help="Contrast multiplier. Defaults to 1.08.",
    )
    parser.add_argument(
        "--color",
        type=float,
        default=1.05,
        help="Color multiplier. Defaults to 1.05.",
    )
    parser.add_argument(
        "--sharpness",
        type=float,
        default=1.18,
        help="Sharpness multiplier. Defaults to 1.18.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    images = iter_images(args.input)
    if not images:
        print(f"No supported images found in {args.input}")
        return 1

    for image_path in images:
        output_path = convert_image(
            image_path,
            args.output,
            args.quality,
            args.contrast,
            args.color,
            args.sharpness,
        )
        print(f"{image_path} -> {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
