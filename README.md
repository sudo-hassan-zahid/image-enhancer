# Image Enhancer

A focused Python CLI for batch-enhancing images and exporting lightweight,
web-ready WEBP assets. It reads from `images/`, improves visual quality with
practical enhancement presets, resizes oversized files, and writes optimized
output to `dist/images/`.

## Purpose

This tool is meant for quick website/app asset preparation:

- Convert JPG, PNG, BMP, TIFF, and WEBP inputs to WEBP.
- Reduce image weight for faster page loads.
- Apply sane quality improvements like autocontrast, color boost, sharpening,
  and optional smoothing.
- Preserve nested folder structure when running recursively.

## Stack

- Python 3
- Pillow for image decoding, enhancement, resizing, and WEBP export
- `argparse` for the CLI interface
- No external services or network calls

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Put source images in `images/`, then run:

```powershell
python enhance_images.py
```

Generated files are written to `dist/images/`.

Useful options:

```powershell
python enhance_images.py --preset crisp --quality 78 --max-width 1600 --max-height 1600
python enhance_images.py --recursive --force
python enhance_images.py --dry-run
python enhance_images.py --list-presets
```

## Presets

- `natural`: light polish for realistic photos
- `punchy`: stronger contrast and color for web assets
- `crisp`: sharper edges for product-style images
- `max-clean`: light smoothing plus sharpening for noisy images

## Output

By default, output files are:

- WEBP format
- Maximum `1920x1920`
- Quality `82`
- Written to `dist/images/`
- Skipped if already present unless `--force` is used

## Limitations

- Enhancement is preset-based, not AI super-resolution.
- Very aggressive sharpening can make low-quality source images look harsh.
- Animated images are not handled as animations; Pillow will process the opened
  frame.
- Color management is basic and depends on Pillow's decoding behavior.
- Existing filenames with the same stem can collide in non-recursive mode.
