#!/usr/bin/env python3
"""Convert images from ./images to optimized WEBP files."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


@dataclass(frozen=True)
class EnhancementPreset:
    contrast: float
    color: float
    sharpness: float
    unsharp_radius: float
    unsharp_percent: int
    unsharp_threshold: int


PRESETS = {
    "natural": EnhancementPreset(1.06, 1.03, 1.12, 1.2, 115, 4),
    "punchy": EnhancementPreset(1.12, 1.10, 1.22, 1.4, 145, 3),
    "crisp": EnhancementPreset(1.08, 1.04, 1.35, 1.1, 165, 2),
    "max-clean": EnhancementPreset(1.10, 1.06, 1.25, 1.6, 150, 5),
}


class Style:
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def paint(text: str, color: str) -> str:
    return f"{color}{text}{Style.RESET}"


def format_bytes(size: int) -> str:
    units = ("B", "KB", "MB", "GB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} {unit}"
        value /= 1024
    return f"{size} B"


def format_savings(before: int, after: int) -> str:
    if before <= 0:
        return "n/a"
    saved_percent = max(0.0, (1 - after / before) * 100)
    return f"{saved_percent:.1f}% smaller"


def iter_images(source_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in source_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def resize_for_web(image: Image.Image, max_width: int | None, max_height: int | None) -> Image.Image:
    if max_width is None and max_height is None:
        return image

    width, height = image.size
    target_width = max_width or width
    target_height = max_height or height

    if width <= target_width and height <= target_height:
        return image

    resized = image.copy()
    resized.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
    return resized


def enhance_image(
    image: Image.Image,
    preset: EnhancementPreset,
) -> Image.Image:
    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Contrast(image).enhance(preset.contrast)
    image = ImageEnhance.Color(image).enhance(preset.color)
    image = ImageEnhance.Sharpness(image).enhance(preset.sharpness)
    return image.filter(
        ImageFilter.UnsharpMask(
            radius=preset.unsharp_radius,
            percent=preset.unsharp_percent,
            threshold=preset.unsharp_threshold,
        )
    )


def convert_image(
    input_path: Path,
    output_dir: Path,
    quality: int,
    max_width: int | None,
    max_height: int | None,
    preset: EnhancementPreset,
) -> Path:
    output_path = output_dir / f"{input_path.stem}.webp"

    with Image.open(input_path) as image:
        image = ImageOps.exif_transpose(image)
        has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
        image = image.convert("RGBA" if has_alpha else "RGB")
        image = resize_for_web(image, max_width, max_height)
        image = enhance_image(image, preset)
        save_options = {
            "format": "WEBP",
            "quality": quality,
            "method": 6,
            "optimize": True,
        }
        if has_alpha:
            save_options["lossless"] = False
            save_options["exact"] = True
        image.save(output_path, **save_options)

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
        "--max-width",
        type=int,
        default=1920,
        help="Maximum output width in pixels. Defaults to 1920.",
    )
    parser.add_argument(
        "--max-height",
        type=int,
        default=1920,
        help="Maximum output height in pixels. Defaults to 1920.",
    )
    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS),
        default="punchy",
        help="Enhancement preset. Defaults to punchy.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    preset = PRESETS[args.preset]

    images = iter_images(args.input)
    if not images:
        print(f"No supported images found in {args.input}")
        return 1

    started = perf_counter()
    total_before = 0
    total_after = 0

    print(paint("Image Enhancer", Style.BOLD))
    print(
        paint("mode", Style.DIM)
        + f" preset={args.preset} quality={args.quality} max={args.max_width}x{args.max_height}"
    )

    for index, image_path in enumerate(images, start=1):
        output_path = convert_image(
            image_path,
            args.output,
            args.quality,
            args.max_width,
            args.max_height,
            preset,
        )
        before = image_path.stat().st_size
        after = output_path.stat().st_size
        total_before += before
        total_after += after
        print(
            f"{paint(f'[{index}/{len(images)}]', Style.CYAN)} "
            f"{image_path.name} -> {output_path.name} "
            f"{paint(format_bytes(before), Style.DIM)} -> "
            f"{paint(format_bytes(after), Style.GREEN)} "
            f"({format_savings(before, after)})"
        )

    elapsed = perf_counter() - started
    print(
        paint("done", Style.GREEN)
        + f" {len(images)} image(s), {format_bytes(total_before)} -> "
        + f"{format_bytes(total_after)} in {elapsed:.2f}s"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
