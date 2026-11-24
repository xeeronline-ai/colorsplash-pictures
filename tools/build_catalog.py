#!/usr/bin/env python3
"""Prepares uploaded pictures for the Color Splash app.

Run by the GitHub Action after every change under pictures/. For each PNG or
JPG in pictures/<category>/ it:
  * fixes the name (lowercase, words joined by "_"),
  * shrinks it to 1024 px and saves it as WebP next to it,
  * moves the original to originals/<category>/ (the app never downloads it).
Then it writes catalog.json, the list the app reads. Pictures named in
free.txt are free; every other picture is locked in the app.

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
FREE = ROOT / 'free.txt'

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


def read_free() -> set:
    """`animals/happy_lion` lines; `#` starts a comment."""
    if not FREE.exists():
        return set()
    free = set()
    for line in FREE.read_text().splitlines():
        line = line.split('#')[0].strip().removesuffix('.png').removesuffix('.webp')
        if '/' in line:
            category, name = line.split('/', 1)
            free.add(f'{clean(category)}/{clean(name)}')
    return free


def write_catalog() -> bool:
    free = read_free()
    pictures = []
    for path in sorted(PICTURES.glob('*/*.webp')):
        entry = {
            'category': path.parent.name,
            'name': path.stem,
            'path': path.relative_to(ROOT).as_posix(),
            'hash': hashlib.sha256(path.read_bytes()).hexdigest()[:16],
        }
        if f'{path.parent.name}/{path.stem}' in free:
            entry['free'] = True
        pictures.append(entry)
    CATALOG.write_text(json.dumps({'version': 1, 'pictures': pictures}, indent=2) + '\n')
    listed = {f"{p['category']}/{p['name']}" for p in pictures}
    for missing in sorted(free - listed):
        print(f'free.txt: no picture called {missing}')
    print(f'catalog.json lists {len(pictures)} pictures, {sum(1 for p in pictures if p.get("free"))} free')
    return not (free - listed)


if __name__ == '__main__':
    ok = prepare()
    ok = write_catalog() and ok
    # Fail the Action so a skipped upload shows a red cross on GitHub.
    sys.exit(0 if ok else 1)
