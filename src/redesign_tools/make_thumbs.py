"""Regenerate the shared photo thumbnails used by the redesign prototypes.

Writes public/assets/redesigns/thumbs/<folder>-<name>.thumb.jpg (max 720px) for the
portraits, the lore photo, the travel photos and the experience galleries. The
".thumb.jpg" suffix keeps these basenames from ending with an original photo's basename,
which matters because optimize_images.py rewrites references by basename.

usage (from the repo root): python src/redesign_tools/make_thumbs.py   (needs Pillow)
"""

import glob
import os
import re

from PIL import Image, ImageOps

OUT = "public/assets/redesigns/thumbs"
SOURCES = (
    ["public/assets/me.jpg", "public/assets/me_alt.jpg"]
    + glob.glob("public/assets/lore/*.jp*g")
    + glob.glob("public/assets/travel/*")
    + glob.glob("public/assets/experience/pics_*/*")
)
FOLDER_NAMES = {"assets": "me", "pics_nvidia": "nvidia", "pics_adtran": "adtran", "pics_gatorai": "gatorai"}


def thumb_name(path):
    folder = os.path.basename(os.path.dirname(path))
    base = os.path.splitext(os.path.basename(path))[0]
    slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
    return f"{FOLDER_NAMES.get(folder, folder)}-{slug}.thumb.jpg"


os.makedirs(OUT, exist_ok=True)
for path in sorted(SOURCES):
    if os.path.splitext(path)[1].lower() not in (".jpg", ".jpeg", ".png"):
        continue
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    im.thumbnail((720, 720), Image.LANCZOS)
    im.save(os.path.join(OUT, thumb_name(path)), quality=78, optimize=True, progressive=True)
    print(thumb_name(path))
