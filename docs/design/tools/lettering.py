"""Lettering that ships as an image (plan v2, 3.6). The fonts never enter static/ or a commit.

python lettering.py <repo> name <tamanegi-kaisho-geki-free-v7.ttf>
python lettering.py <repo> chongsha <Bakudai-Bold.ttf>
python lettering.py <repo> icon <tamanegi-kaisho-geki-free-v7.ttf>

Each output is white + alpha, coloured by CSS mask so the night edition recolours it; the tab icon
(assets/media/icon.png, read by Blox) is the one exception: ink 達 on a paper rounded square, fixed colours.
"""
import sys, pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

repo = pathlib.Path(sys.argv[1]); what = sys.argv[2]; font = sys.argv[3]
out = repo / "static/textures"

def render(text, size, track, name):
    f = ImageFont.truetype(font, size)
    W = int(size * (len(text) + 1)); H = int(size * 1.6)
    im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
    x = size // 4
    for ch in text:
        d.text((x, size // 4), ch, font=f, fill=255)
        x += d.textlength(ch, font=f) + track * size
    im = im.crop(im.getbbox())
    pad = int(size * .03)
    canvas = Image.new("L", (im.width + 2 * pad, im.height + 2 * pad), 0); canvas.paste(im, (pad, pad))
    white = Image.new("L", canvas.size, 255)
    Image.merge("LA", (white, canvas)).save(out / name, optimize=True)
    print(f"{name:24} {canvas.size} {(out / name).stat().st_size / 1024:.1f} KB")

if what == "name":
    render("陳威達", 160, 0.0, "name-chen-weida.png")     # shown about 40 CSS px tall: 4x
elif what == "chongsha":
    render("衝啥", 360, 0.04, "chongsha.png")
elif what == "icon":                                       # UD's pick, 2026-11-16
    from PIL import ImageDraw as D
    N = 512; paper, ink = (0xE2, 0xDD, 0xD1, 255), (0x1B, 0x24, 0x36, 255)
    f = ImageFont.truetype(font, 800)
    g = Image.new("L", (1200, 1200), 0); D.Draw(g).text((200, 120), "達", font=f, fill=255); g = g.crop(g.getbbox())
    k = N * 0.82 / max(g.size); g = g.resize((round(g.width * k), round(g.height * k)), Image.LANCZOS)
    im = Image.new("RGBA", (N, N), paper); im.paste(Image.new("RGBA", g.size, ink), ((N - g.width) // 2, (N - g.height) // 2), g)
    corner = Image.new("L", (N, N), 0); D.Draw(corner).rounded_rectangle((0, 0, N - 1, N - 1), radius=N * 40 // 256, fill=255)
    im.putalpha(corner)
    dest = repo / "assets/media/icon.png"; im.save(dest, optimize=True)
    print(f"icon.png {im.size} {dest.stat().st_size / 1024:.1f} KB")
