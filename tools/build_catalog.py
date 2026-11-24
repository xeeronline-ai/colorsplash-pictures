#!/usr/bin/env python3
"""Prepares uploaded pictures for the Color Splash app.

Run by the GitHub Action after every change under pictures/. For each PNG or
JPG in pictures/<category>/ it:
  * fixes the name (lowercase, words joined by "_"),
  * shrinks it to 1024 px and saves it as WebP next to it,
  * moves the original to originals/<category>/ (the app never downloads it).
Then it writes catalog.json, the list the app reads.

    python3 tools/build_catalog.py

Needs Pillow (pip3 install pillow).
"""

import hashlib
import json
import pathlib
import re
import shutil
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
PICTURES = ROOT / 'pictures'
ORIGINALS = ROOT / 'originals'
CATALOG = ROOT / 'catalog.json'

MAX_SIDE = 1024
QUALITY = 95
SOURCE_TYPES = {'.png', '.jpg', '.jpeg'}


def clean(name: str) -> str:
    """`Happy Lion (2)` -> `happy_lion_2`."""
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')


def convert(path: pathlib.Path, target: pathlib.Path) -> None:
    image = Image.open(path)
    image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
    if image.mode == 'RGBA':
        # Generated art often leaves the subject at alpha 250-254.
        image.putalpha(image.getchannel('A').point(lambda a: 255 if a >= 245 else a))
    if max(image.size) > MAX_SIDE:
        scale = MAX_SIDE / max(image.size)
        image = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, 'WEBP', quality=QUALITY, method=6)


def prepare() -> bool:
    ok = True
    for path in sorted(PICTURES.glob('*/*')):
        if not path.is_file() or path.name.startswith('.'):
            continue
        category, name, suffix = clean(path.parent.name), clean(path.stem), path.suffix.lower()
        if not category or not name:
            print(f'SKIPPED {path.relative_to(ROOT)}: the name needs letters or numbers')
            ok = False
            continue
        target = PICTURES / category / f'{name}.webp'
        if suffix in SOURCE_TYPES:
            try:
                convert(path, target)
            except Exception as error:  # A broken or non-image upload.
                print(f'SKIPPED {path.relative_to(ROOT)}: not a readable picture ({error})')
                ok = False
                continue
            original = ORIGINALS / category / f'{name}{suffix}'
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(path, original)
            print(f'ADDED   {target.relative_to(ROOT)}  {target.stat().st_size // 1024} KB')
        elif suffix == '.webp' and path != target:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(path, target)
            print(f'RENAMED {path.relative_to(ROOT)} -> {target.relative_to(ROOT)}')
        elif suffix != '.webp':
            print(f'SKIPPED {path.relative_to(ROOT)}: upload PNG or JPG pictures only')
            ok = False
    # Folders emptied by renaming.
    for folder in PICTURES.iterdir():
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
    return ok


def write_catalog() -> None:
    pictures = []
    for path in sorted(PICTURES.glob('*/*.webp')):
        pictures.append({
            'category': path.parent.name,
            'name': path.stem,
            'path': path.relative_to(ROOT).as_posix(),
            'hash': hashlib.sha256(path.read_bytes()).hexdigest()[:16],
        })
    CATALOG.write_text(json.dumps({'version': 1, 'pictures': pictures}, indent=2) + '\n')
    print(f'catalog.json lists {len(pictures)} pictures')


if __name__ == '__main__':
    ok = prepare()
    write_catalog()
    # Fail the Action so a skipped upload shows a red cross on GitHub.
    sys.exit(0 if ok else 1)
