"""Generate the site favicons from a 16x16 pixel-art grid ("pixel andy").

Writes:
  public/favicon.svg           crisp vector version (used by modern browsers)
  public/favicon.ico           16/32/48 px fallback (legacy browsers, /favicon.ico requests)
  public/apple-touch-icon.png  180 px home-screen icon for iOS (full square; iOS rounds it)

Edit GRID / PALETTE and rerun from the repo root: python src/make_favicon.py  (needs Pillow)
"""

from PIL import Image, ImageDraw

GRID = [
    "................",
    ".....BBBBBB.....",
    "....BbbbbbbB....",
    "...BbbbbbbbbB...",
    "..BYYbYYbYYbYB..",
    "..BBBBBBBBBBBB..",
    "..EKKKKKKKKKKE..",
    "..KKEEKKKKEEKK..",
    "..KKKKKKKKKKKK..",
    "..kKKKKKKKKKKk..",
    "...KKMKKKKMKK...",
    "...kKKMMMMKKk...",
    "....kKKKKKKk....",
    "......kkkk......",
    "..WWWWWkkWWWWW..",
    ".WWWWWWWWWWWWWW.",
]
PALETTE = {
    ".": "#a9c3e3",  # sky
    "B": "#4a2e1b",  # beanie, dark
    "b": "#6b4426",  # beanie
    "Y": "#d39a3a",  # beanie stripe
    "E": "#231812",  # eyes, hair
    "K": "#e0ab86",  # skin
    "k": "#c38b68",  # skin shadow
    "M": "#8e3f36",  # smile
    "W": "#f4f4f2",  # shirt
}
CORNER = 2.5  # corner radius in grid pixels (for the svg and ico)

assert len(GRID) == 16 and all(len(row) == 16 for row in GRID)


def svg():
    rects = []
    for y, row in enumerate(GRID):
        x = 0
        while x < 16:
            ch = row[x]
            run = 1
            while x + run < 16 and row[x + run] == ch:
                run += 1
            rects.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="{PALETTE[ch]}"/>')
            x += run
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges">\n'
        f'<clipPath id="c"><rect width="16" height="16" rx="{CORNER}"/></clipPath>\n'
        '<g clip-path="url(#c)">\n' + "\n".join(rects) + "\n</g>\n</svg>\n"
    )


def bitmap(size, rounded):
    base = Image.new("RGB", (16, 16))
    for y, row in enumerate(GRID):
        for x, ch in enumerate(row):
            base.putpixel((x, y), tuple(int(PALETTE[ch][i:i + 2], 16) for i in (1, 3, 5)))
    im = base.resize((size, size), Image.NEAREST).convert("RGBA")
    if rounded:
        mask = Image.new("L", (size, size), 0)
        r = round(CORNER * size / 16)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), r, fill=255)
        im.putalpha(mask)
    return im


with open("public/favicon.svg", "w", encoding="utf-8") as f:
    f.write(svg())

icons = [bitmap(s, rounded=True) for s in (48, 32, 16)]
icons[0].save("public/favicon.ico", format="ICO", sizes=[(48, 48), (32, 32), (16, 16)], append_images=icons[1:])

bitmap(180, rounded=False).convert("RGB").save("public/apple-touch-icon.png", optimize=True)
print("wrote public/favicon.svg, public/favicon.ico, public/apple-touch-icon.png")
