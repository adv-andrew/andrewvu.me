"""Tile atlas + tile table for the /mosaic redesign prototype.

The mosaic portrait on /mosaic is built in the browser from these tiles. Each of the
41 homepage photos (the two portraits, the first-pc photo, 17 travel photos and the
21 experience-gallery photos) is cut into ~10 square crops ("variants") so the
colour matcher has more to choose from, while every tile still shows one real photo.

Outputs (public/assets/redesigns/mosaic/):
  mosaic-atlas.v1.jpg   every variant as a 64px tile in a 66px slot (1px extruded
                        gutter so bilinear sampling never bleeds into a neighbour)
  mosaic-tiles.v1.json  per variant: photo index, crop rect (normalised to the
                        photo, so the page can redraw it sharp from the photo's
                        thumb when zoomed in) and a 3x3 CIE Lab colour signature

Photo order = the order the page builds its photo list in (mosaic.html, script section 1):
  photo, photo_alt, origin, travel[...], galleries.gatorai, .adtran, .nvidia
`keys` in the JSON lets the page check that the two orders still agree.

usage:
  python src/redesign_tools/mosaic_assets.py [--copy-to <preview>/assets/redesigns/mosaic]
"""

import argparse
import json
import os
import shutil

from jinja2 import Environment, FileSystemLoader
from PIL import Image

HERE = os.path.dirname(os.path.realpath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
TEMPLATES = os.path.join(REPO, "src", "templates")
PUBLIC = os.path.join(REPO, "public")
OUT_DIR = os.path.join(PUBLIC, "assets", "redesigns", "mosaic")
ATLAS_NAME = "mosaic-atlas.v1.jpg"
TABLE_NAME = "mosaic-tiles.v1.json"

TILE = 64          # tile content size in the atlas
SLOT = TILE + 2    # + 1px extruded gutter on every side
ATLAS_COLS = 24
JPEG_QUALITY = 80


def load_photos():
    env = Environment(loader=FileSystemLoader(TEMPLATES))
    d = env.get_template("redesigns/data.html").module
    thumbs = [d.photo_thumb, d.photo_alt_thumb, d.origin["thumb"]]
    thumbs += [t["thumb"] for t in d.travel]
    for gid in ("gatorai", "adtran", "nvidia"):
        thumbs += [p["thumb"] for p in d.galleries[gid]["photos"]]
    photos = []
    for t in thumbs:
        base = os.path.basename(t)
        key = base.split(".thumb")[0]
        photos.append({"key": key, "path": os.path.join(PUBLIC, t.lstrip("/"))})
    return photos


def crop_rects(w, h):
    """Square crops as (x, y, side) in pixels: the full centre square, the ends of
    long photos, a 72% ring and four 50% quadrant crops."""
    s = min(w, h)
    rects = []

    def add(scale, tx, ty):
        side = s * scale
        x = (w - side) * tx
        y = (h - side) * ty
        for (ox, oy, os_) in rects:  # skip near-duplicates
            if abs(ox - x) < side * 0.12 and abs(oy - y) < side * 0.12 and abs(os_ - side) < side * 0.12:
                return
        rects.append((x, y, side))

    add(1.0, 0.5, 0.5)
    add(1.0, 0.0, 0.0)
    add(1.0, 1.0, 1.0)
    for tx, ty in ((0.5, 0.5), (0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)):
        add(0.72, tx, ty)
    for tx, ty in ((0.2, 0.2), (0.8, 0.2), (0.2, 0.8), (0.8, 0.8)):
        add(0.5, tx, ty)
    return rects


def srgb_to_lab(r, g, b):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    rl, gl, bl = lin(r), lin(g), lin(b)
    x = (rl * 0.4124 + gl * 0.3576 + bl * 0.1805) / 0.95047
    y = rl * 0.2126 + gl * 0.7152 + bl * 0.0722
    z = (rl * 0.0193 + gl * 0.1192 + bl * 0.9505) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--copy-to", help="also copy the outputs into this folder (e.g. a preview dir)")
    args = ap.parse_args()

    photos = load_photos()
    assert len(photos) == 41, len(photos)

    tiles = []  # (photo index, rect normalised, tile image)
    for pi, p in enumerate(photos):
        im = Image.open(p["path"]).convert("RGB")
        w, h = im.size
        for (x, y, side) in crop_rects(w, h):
            box = (round(x), round(y), round(x + side), round(y + side))
            tile = im.crop(box).resize((TILE, TILE), Image.LANCZOS)
            rect = (box[0] / w, box[1] / h, (box[2] - box[0]) / w, (box[3] - box[1]) / h)
            tiles.append((pi, rect, tile))

    n = len(tiles)
    rows = (n + ATLAS_COLS - 1) // ATLAS_COLS
    atlas = Image.new("RGB", (ATLAS_COLS * SLOT, rows * SLOT), (128, 128, 128))
    table_t, table_s = [], []
    for i, (pi, rect, tile) in enumerate(tiles):
        cx, cy = (i % ATLAS_COLS) * SLOT, (i // ATLAS_COLS) * SLOT
        atlas.paste(tile.resize((SLOT, SLOT), Image.NEAREST), (cx, cy))  # extruded gutter
        atlas.paste(tile, (cx + 1, cy + 1))
        table_t += [pi] + [round(v * 10000) for v in rect]
        small = tile.resize((3, 3), Image.BOX).load()
        for k in range(9):
            L, A, B = srgb_to_lab(*small[k % 3, k // 3])
            table_s += [round(L), round(A), round(B)]

    os.makedirs(OUT_DIR, exist_ok=True)
    atlas_path = os.path.join(OUT_DIR, ATLAS_NAME)
    table_path = os.path.join(OUT_DIR, TABLE_NAME)
    atlas.save(atlas_path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    table = {
        "v": 1,
        "tile": TILE,
        "slot": SLOT,
        "cols": ATLAS_COLS,
        "count": n,
        "keys": [p["key"] for p in photos],
        "t": table_t,  # per tile: photo index, x, y, w, h (crop, x10000 of the photo size)
        "s": table_s,  # per tile: 3x3 cells x (L, a, b), row-major
    }
    with open(table_path, "w", encoding="utf-8") as f:
        json.dump(table, f, separators=(",", ":"))

    for pth in (atlas_path, table_path):
        print(f"{os.path.relpath(pth, REPO)}  {os.path.getsize(pth) / 1024:.0f} KB")
    print(f"{n} tiles from {len(photos)} photos, atlas {atlas.size[0]}x{atlas.size[1]}")

    if args.copy_to:
        os.makedirs(args.copy_to, exist_ok=True)
        for pth in (atlas_path, table_path):
            shutil.copy2(pth, args.copy_to)
        print(f"copied to {args.copy_to}")


if __name__ == "__main__":
    main()
