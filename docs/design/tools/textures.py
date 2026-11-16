"""Paper textures for the udchen.tw redesign. All outputs go to <repo>/static/textures/.
Deterministic (fixed seeds).

python textures.py <repo> night
    The night fibre layer: newsprint-fibres.webp with its brightest flecks capped, so soft-light on the
    dark paper never lifts a pixel past the night ceiling (paper_contrast.py dark).
python textures.py <repo> sheet <Paper005_2K-JPG_Displacement.jpg>
    Creases (ambientCG Paper 005, CC0) and the worn sheet edges (plan v2, 3.4).
python textures.py <repo> <Paper002_Color.jpg> [<reading font.ttf> <display font.ttf>]
    Base layers: fibres, tone, show-through, press specks.
The display wear masks this script used to make were replaced by the SVG ink filters (plan v2, 3.3).
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


# ---------------------------------------------------------------- sheet -------
def lum(rgb):
    """Relative luminance (WCAG) of sRGB values 0..1."""
    c = np.asarray(rgb, np.float64)
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return lin @ np.array([0.2126, 0.7152, 0.0722])

PAPER = np.array([0xE2, 0xDD, 0xD1]) / 255.0
FLOOR = 0.423            # plan 3.4: lowest paper luminance inside the content column

def creases(disp_path):
    g = np.asarray(Image.open(disp_path).convert("L"), np.float32) / 255.0     # 2048², seamless
    neutral = float(np.median(g))                 # the flat sheet: no change there
    # Shadow only (plan 3.4): darker than neutral darkens, lighter is no change. Strength as the
    # approved mock (hard-light at contrast 1.7, opacity .7 => slope 3.4 below neutral, x .7).
    dark = np.clip(3.4 * (neutral - g), 0, 1) * 0.7
    m = 1 - dark                                   # multiply factor on the paper
    # Floor: the lowest factor that keeps paper luminance >= FLOOR (+ headroom for the fibre and
    # tone layers, which the full-page check measures).
    lo, hi = 0.5, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if lum(PAPER * mid) < FLOOR + HEADROOM: lo = mid
        else: hi = mid
    floor = hi
    # Soft knee, not a clip: a hard clip flattens the deepest creases into flat grey patches.
    # Darkness up to KNEE of the budget is kept as is; beyond it, compressed smoothly toward
    # the floor, so every crease keeps its relief and none goes past the floor.
    budget = 1 - floor; k = KNEE * budget
    d = 1 - m
    d = np.where(d <= k, d, k + (budget - k) * np.tanh((d - k) / (budget - k)))
    edge = 1 - d
    # Centre: only the deepest creases, faint.
    deep = np.clip((1 - m) - CENTRE_T, 0, None) * CENTRE_K
    centre = np.maximum(1 - deep, CENTRE_FLOOR)
    print(f"neutral {neutral:.3f}  floor factor {floor:.3f} (paper L {lum(PAPER*floor):.3f})  "
          f"compressed (beyond the knee) {np.mean((1 - m) > k)*100:.2f}%  centre active {np.mean(deep > 0)*100:.2f}%")
    for a, name in [(edge, "crease-edge.webp"), (centre, "crease-centre.webp")]:
        im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8), "L").resize((1500, 1500), Image.LANCZOS)
        im.save(out / name, quality=82, method=6)
        print(f"{name:28} {(out / name).stat().st_size // 1024} KB")
    # Over dark areas (footer images, the night edition) creases lighten instead (3.4): an alpha mask
    # of crease depth (1 = deepest), painted in paper colour at low opacity by CSS.
    # Only real creases (flat paper is 0, which also keeps the file small); half resolution, shown at
    # the same tile size.
    depth = np.clip(((1 - m) - 0.06) / 0.45, 0, 1)
    a = np.asarray(Image.fromarray((depth * 255).astype(np.uint8), "L").resize((750, 750), Image.LANCZOS))
    Image.merge("RGBA", (Image.new("L", (750, 750), 255),) * 3 + (Image.fromarray(a, "L"),)).save(out / "crease-light.webp", quality=70, method=6)
    print(f"{'crease-light.webp':28} {(out / 'crease-light.webp').stat().st_size // 1024} KB")

def walk(n, depth, seed, step):
    """Worn edge: a random walk inside [0.12, 1] x depth, a few px of jitter, seamless."""
    r = np.random.default_rng(seed); x = depth * .45; pts = []
    for _ in range(n):
        x += (r.random() - .5) * depth * .35
        if r.random() < .06: x += (r.random() - .3) * depth * .9
        x = max(depth * .12, min(depth, x)); pts.append(x)
    pts[-1] = pts[0]
    return pts

def svg(w, h, body):
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>{body}</svg>\n"

def edges(tag, L, R, T):
    """Masks (black = shown) for the sheet's left, right and top edges. CSS colours them."""
    H = 918; ys = list(range(0, H + 1, 9))
    xs = walk(len(ys), L, 5, 9)
    poly = " ".join(f"{x:.1f},{y}" for x, y in zip(xs, ys))
    (out / f"edge-left-{tag}.svg").write_text(svg(L, H, f"<polygon points='0,0 {poly} 0,{H}'/>"))
    # Right: the top sheet's edge, two more page edges behind it (4.5 px apart), then the surround.
    H = 1035; ys = list(range(0, H + 1, 9)); D = R - 10
    xs = walk(len(ys), D, 7, 9)
    edge = lambda i: [min(R, x + D * .1 + i * 4.5) for x in xs]
    pts = lambda xx: " ".join(f"{R - x:.1f},{y}" for x, y in zip(xx, ys))   # mirrored: sheet on the left
    outer = edge(2)
    (out / f"edge-right-surround-{tag}.svg").write_text(svg(R, H, f"<polygon points='{R},0 {pts(outer)} {R},{H}'/>"))
    (out / f"edge-right-pages-{tag}.svg").write_text(svg(R, H, f"<polygon points='{pts(edge(0))} " + " ".join(f"{R - x:.1f},{y}" for x, y in reversed(list(zip(outer, ys)))) + "'/>"))
    lines = "".join(f"<polyline fill='none' stroke='black' stroke-width='.7' points='{pts(edge(i))}'/>" for i in (0, 1, 2))
    (out / f"edge-right-lines-{tag}.svg").write_text(svg(R, H, lines))
    # Top: same walk, horizontal.
    W = 1000; xs2 = list(range(0, W + 1, 10)); ys2 = walk(len(xs2), T, 11, 10)
    (out / f"edge-top-{tag}.svg").write_text(svg(W, T, f"<polygon points='0,0 " + " ".join(f"{x},{y:.1f}" for x, y in zip(xs2, ys2)) + f" {W},0'/>"))
    print("edges", tag, L, R, T)

HEADROOM, KNEE, CENTRE_T, CENTRE_K, CENTRE_FLOOR = 0.16, 0.5, 0.20, 0.5, 0.95
if scan == "night":
    # Soft-light over #111A2B with the tone (max 142) and show-through (max 130) layers: a fibre value of
    # 152 gives relative luminance 0.0245, under the 0.028 at which night ink-2 drops below 4.5:1.
    f = np.asarray(Image.open(out / "newsprint-fibres.webp").convert("L"), np.float32)
    # Capped at 140 and saved lossy at q90: compression lifts some values again, and the saved file
    # must stay at or under 152 (checked below).
    capped = np.minimum(f, 140)
    print(f"night fibres: {np.mean(f > 140) * 100:.2f}% of pixels capped")
    Image.fromarray(capped.astype(np.uint8), "L").save(out / "newsprint-fibres-night.webp", quality=90)
    back = np.asarray(Image.open(out / "newsprint-fibres-night.webp").convert("L"))
    assert back.max() <= 152, back.max()
    print("newsprint-fibres-night.webp", (out / "newsprint-fibres-night.webp").stat().st_size // 1024, "KB, max", back.max())
    sys.exit(0)
if scan == "sheet":
    creases(sys.argv[3])
    edges("wide", 22, 32, 12)      # >= 641 px
    edges("narrow", 9, 19, 6)      # < 641 px
    sys.exit(0)

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
