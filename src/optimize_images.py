# /usr/bin/env python3

import os
import subprocess
from threading import Thread, Lock
from glob import glob


successful_conversions = []
lock = Lock()


def is_img(fname: str):
    ext = os.path.splitext(fname)[1].lower()
    return ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]


def optimized_name(fname: str):
    return fname + ".webp"


def optimize_image(fname: str):
    outname = optimized_name(fname)
    result = subprocess.run(["cwebp", "-q", "80", fname, "-o", outname, "-quiet"])

    if result.returncode != 0:
        print(f"Skipped {fname} (cwebp failed)")
        return

    os.remove(fname)

    with lock:
        successful_conversions.append(os.path.basename(fname))

    print(f"Optimized {fname}")


imgs = [f for f in glob("dist/assets/**/*", recursive=True) if is_img(f)]
img_threads = []

for img in imgs:
    t = Thread(target=optimize_image, args=(img,))
    t.start()
    img_threads.append(t)

# Wait for all image conversions to complete
for t in img_threads:
    t.join()


def replace_in_html(html: str, img_basenames: list):
    with open(html, "r") as f:
        content = f.read()

    for img in img_basenames:
        content = content.replace(img, optimized_name(img))

    with open(html, "w") as f:
        f.write(content)

    print(f"Replaced in {html}")


# Only replace references for successfully converted images
htmls = [f for f in glob("dist/**/*.html", recursive=True)]
html_threads = []

for html in htmls:
    t = Thread(target=replace_in_html, args=(html, successful_conversions))
    t.start()
    html_threads.append(t)

for t in html_threads:
    t.join()
