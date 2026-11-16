"""Paper, press and halftone textures for the udchen.tw redesign.

python textures.py <repo> <Paper002_Color.jpg>
All outputs go to <repo>/static/textures/. Deterministic (fixed seeds).
"""
import sys, pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

repo = pathlib.Path(sys.argv[1]); scan = sys.argv[2]
out = repo / "static/textures"
rng = np.random.default_rng(1916)

def save_gray(a, name):
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "L").save(out / name, optimize=True)
    print(f"{name:28} {(out / name).stat().st_size // 1024} KB")

def save_alpha(alpha, name, levels=None):
    """White RGB + alpha: used only as CSS masks, so colour comes from tokens.
    levels: quantise alpha (2 = crisp 1-bit edges, which is also what keeps files small)."""
    if levels: alpha = np.round(np.clip(alpha, 0, 1) * (levels - 1)) / (levels - 1)
    a = np.clip(alpha * 255, 0, 255).astype(np.uint8)
    img = Image.fromarray(a, "L").convert("LA")
    img.putalpha(Image.fromarray(a, "L"))
    rgba = Image.merge("RGBA", (Image.new("L", img.size, 255),) * 3 + (img.getchannel("A"),))
    if levels:
        q = Image.fromarray(a, "L").point(lambda v: v)  # palette PNG with alpha
        pal = rgba.quantize(colors=levels, method=Image.Quantize.FASTOCTREE)
        pal.save(out / name, optimize=True, transparency=None)
        rgba2 = Image.open(out / name).convert("RGBA")
        if np.abs(np.asarray(rgba2)[..., 3].astype(int) - a.astype(int)).max() > 2:
            rgba.save(out / name, optimize=True)
    else:
        rgba.save(out / name, optimize=True)
    print(f"{name:28} {(out / name).stat().st_size // 1024} KB")

def wrap_blur(a, s):
    return ndi.gaussian_filter(a, s, mode="wrap")

# ---------------------------------------------------------------- paper -------
g = np.asarray(Image.open(scan).convert("L"), dtype=np.float32) / 255.0   # 2048 x 1588, seamless
hp = g - wrap_blur(g, 20)                       # remove PBR shading / low frequencies
sd = hp.std()
# Coring: drop the fine sand-like grain, keep fibres and flecks (they stand above it).
core = np.sign(hp) * np.maximum(np.abs(hp) - 0.9 * sd, 0)
fib = 128 + core * 900                          # gray-centred, used with soft-light
Image.fromarray(np.clip(fib, 0, 255).astype(np.uint8), "L").resize((794, 1024), Image.LANCZOS).save(out / "newsprint-fibres.webp", quality=82)
print("newsprint-fibres.webp", (out / "newsprint-fibres.webp").stat().st_size // 1024, "KB")

# Slightly uneven tone, very low frequency (shown at 1600px; no blotches).
n = wrap_blur(rng.standard_normal((400, 400)).astype(np.float32), 38)
n = n / np.abs(n).max()
save_gray(128 + n * 14, "newsprint-tone.png")

# Show-through: the reverse page's print, mirrored, softened by the sheet itself.
W, H = 1400, 1900
st = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(st)
font = ImageFont.truetype(sys.argv[3], 15) if len(sys.argv) > 3 else ImageFont.load_default()
head = ImageFont.truetype(sys.argv[4], 58) if len(sys.argv) > 4 else font
letters = "etaoinshrdlucmfwypvbgk"
cols = [(60, 380), (410, 720), (750, 1060), (1090, 1340)]
y0 = 70
d.text((60, 40), "".join(rng.choice(list(letters), 18)), font=head, fill=255)
for ci, (x0, x1) in enumerate(cols):
    y = 160 + ci * 37 % 90
    while y < H - 40:
        if rng.random() < 0.05:                       # a ghost photo block
            h = int(rng.integers(140, 260)); d.rectangle((x0, y, x1, y + h), fill=110); y += h + 24; continue
        if rng.random() < 0.06:                       # a mid head
            d.text((x0, y), "".join(rng.choice(list(letters), int(rng.integers(6, 12)))), font=head.font_variant(size=30), fill=255); y += 46; continue
        words, x = [], x0
        line = ""
        while True:
            w = "".join(rng.choice(list(letters), int(rng.integers(2, 9))))
            if d.textlength(line + w + " ", font=font) > x1 - x0: break
            line += w + " "
        d.text((x0, y), line, font=font, fill=255); y += 21
st = np.asarray(st.transpose(Image.FLIP_LEFT_RIGHT), dtype=np.float32) / 255.0
st = ndi.gaussian_filter(st, 1.3)
Image.fromarray(np.clip(128 - st * 10, 0, 255).astype(np.uint8), "L").resize((700, 950), Image.LANCZOS).save(out / "newsprint-show.webp", quality=80)
print("newsprint-show.webp", (out / "newsprint-show.webp").stat().st_size // 1024, "KB")

# ---------------------------------------------------------------- press -------
# Specks knocked out of the ink + the paper's own light fibres showing through it.
# Tile 1024 shown at 512 CSS px (2x).
T = 1024
light = np.maximum(hp[:T, :T] - 1.6 * sd, 0)
light = np.clip(light / (light.max() * 0.35), 0, 1)
clus = wrap_blur(rng.standard_normal((T, T)).astype(np.float32), 60)
clus = (clus - clus.min()) / (clus.max() - clus.min())          # uneven patches

def specks(count, rmax, seed):
    r = np.random.default_rng(seed)
    m = np.zeros((T, T), np.float32)
    pts = r.random((count * 4, 2)) * T
    keep = r.random(count * 4) < clus[pts[:, 1].astype(int), pts[:, 0].astype(int)] ** 2.2
    pts = pts[keep][:count]
    yy, xx = np.mgrid[-4:5, -4:5]
    for (x, y), rad in zip(pts, r.uniform(0.5, rmax, len(pts))):
        disk = np.clip(rad + 0.5 - np.hypot(xx + r.normal(0, .3), yy + r.normal(0, .3)), 0, 1)
        xi, yi = int(x), int(y)
        sl = (slice(max(yi - 4, 0), min(yi + 5, T)), slice(max(xi - 4, 0), min(xi + 5, T)))
        dy, dx = sl[0].start - (yi - 4), sl[1].start - (xi - 4)
        sub = disk[dy:dy + sl[0].stop - sl[0].start, dx:dx + sl[1].stop - sl[1].start]
        m[sl] = np.maximum(m[sl], sub)
    return m

save_alpha(np.maximum(specks(1700, 1.6, 1), light * 0.55), "press-light.png", levels=4)
save_alpha(np.maximum(specks(3200, 2.0, 2), light * 0.75), "press-medium.png", levels=4)

# ---------------------------------------------------------------- wear --------
# Display wear masks. Tile = 12em at 100 px/em; opaque keeps ink, transparent is a hole.
# Largest hole 0.06em (narrower than a stroke at every display size).
WT = 1200
def wear(seed, pits, scratches, fibre_k):
    r = np.random.default_rng(seed)
    c = wrap_blur(r.standard_normal((WT, WT)).astype(np.float32), 90)
    c = (c - c.min()) / (c.max() - c.min())
    hole = Image.new("L", (WT, WT), 0); dd = ImageDraw.Draw(hole)
    for _ in range(pits):
        x, y = r.random(2) * WT
        if r.random() > c[int(y), int(x)] ** 1.5: continue
        rad = r.uniform(0.6, 3.0)
        pts = [(x + rad * np.cos(t) * r.uniform(.6, 1.2), y + rad * np.sin(t) * r.uniform(.6, 1.2))
               for t in np.linspace(0, 2 * np.pi, 7)[:-1]]
        dd.polygon(pts, fill=255)
    for _ in range(scratches):
        x, y = r.random(2) * WT; a = r.uniform(-.5, .5) + (np.pi / 2 if r.random() < .3 else 0)
        ln = r.uniform(8, 30)
        dd.line((x, y, x + ln * np.cos(a), y + ln * np.sin(a)), fill=255, width=int(r.integers(1, 3)))
    h = np.asarray(hole, np.float32) / 255.0
    # fibre-shaped holes from the scan (rotated crop so the three masks differ)
    o = (seed % 4) * 200; crop = np.rot90(hp[o:o + WT, :WT], seed)
    crop = np.resize(crop, (WT, WT))
    fh = np.clip((crop - 1.4 * sd) / (sd * 1.5), 0, 1) * fibre_k
    h = np.maximum(h, fh)
    h = ndi.gaussian_filter(h, 0.6)
    return 1 - np.clip(h * 1.4, 0, 1)

for i in (1, 2, 3):
    save_alpha(wear(i, 2600, 120, 0.7), f"wear-{i}-light.png", levels=2)
    save_alpha(wear(i + 10, 4800, 260, 1.0), f"wear-{i}-medium.png", levels=2)
