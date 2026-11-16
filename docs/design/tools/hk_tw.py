import sys, glob, re, pathlib, numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
repo = pathlib.Path(sys.argv[1]); noto = sys.argv[2]
text = "".join(p.read_text() for p in repo.glob("content/post/*/index.md"))
chars = sorted(set(c for c in text if 0x3400 <= ord(c) <= 0x9FFF))
slices = {}
for f in glob.glob(str(repo / "static/fonts/chiron-sung-*.woff2")):
    for cp in TTFont(f, lazy=True).getBestCmap(): slices.setdefault(cp, f)
def render(font, ch):
    im = Image.new("L", (140, 140), 0); ImageDraw.Draw(im).text((20, 10), ch, font=font, fill=255)
    im = im.crop(im.getbbox()).resize((64, 64), Image.LANCZOS)
    from scipy import ndimage as ndi
    return ndi.gaussian_filter(np.asarray(im, np.float32) / 255, 2.5) > 0.12
nf = ImageFont.truetype(noto, 80)
cache = {}; diff = []
for ch in chars:
    f = slices.get(ord(ch))
    if not f: continue
    if f not in cache: cache[f] = ImageFont.truetype(f, 80)
    a, b = render(nf, ch), render(cache[f], ch)
    d = (a ^ b).sum() / max(a.sum(), 1)
    if d > 0.25: diff.append((d, ch))
diff.sort(reverse=True)
print(len(chars), "distinct Han characters in posts;", len(diff), "drawn differently")
print("".join(c for _, c in diff)); print([round(x,2) for x,_ in diff[:40]])
