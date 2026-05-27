# Image Enhancer

A spicy little Python CLI for turning source images into lightweight, web-ready
WEBP files while applying practical quality enhancement.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Put source images in `images/`, then run:

```bash
python enhance_images.py
```

Generated files are written to `dist/images/`.

Useful options:

```bash
python enhance_images.py --preset crisp --quality 78 --max-width 1600 --max-height 1600
python enhance_images.py --recursive --force
python enhance_images.py --dry-run
python enhance_images.py --list-presets
```

Supported inputs: JPG, JPEG, PNG, BMP, TIFF, and WEBP.
