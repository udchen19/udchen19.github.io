"""Coarse AM halftone plates (alpha masks) for the udchen.tw redesign.

python halftone.py <repo>
Ink plate: navy (or night ink) via CSS mask. Orange plate: second ink, own screen angle.
"""
import sys, pathlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

repo = pathlib.Path(sys.argv[1]); out = repo / "static/textures"

def screen(dark, cell, angle_deg, soft=0.9):
    """dark: 0..1 ink coverage wanted. Returns alpha 0..1 of clustered round dots."""
    h, w = dark.shape
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.deg2rad(angle_deg)
    u = (x * np.cos(a) + y * np.sin(a)) / cell
    v = (-x * np.sin(a) + y * np.cos(a)) / cell
    spot = 0.5 + 0.25 * (np.cos(2 * np.pi * u) + np.cos(2 * np.pi * v))   # 0..1
    thr = 1 - spot
    # edge width ~soft px: scale by local gradient magnitude of the threshold field
    k = cell / (np.pi * soft)
    return np.clip((dark - thr) * k + 0.5, 0, 1)

def save(alpha, name):
    a = Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8), "L")
    white = Image.new("L", a.size, 255)
    Image.merge("RGBA", (white, white, white, a)).save(out / name, optimize=True)
    print(f"{name:26} {a.size} {(out / name).stat().st_size // 1024} KB")

def load(path, width):
    im = Image.open(path).convert("RGB")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    return np.asarray(im, np.float32) / 255.0

def hsv(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn + 1e-6
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return hue, d / (mx + 1e-6), mx

def local_contrast(lum, sigma, amount):
    return np.clip(lum + amount * (lum - ndi.gaussian_filter(lum, sigma)), 0, 1)

# --- 亞太球場 stadium: 3:1 slot, ~960 CSS px wide -> 1920 px (2x), cell 10 px = 5 CSS px
rgb = load(repo / "static/textures/stadium-g2-color.jpg", 1920)
H = rgb.shape[0]; crop_h = 1920 // 3
top = int(H * 0.36)                           # keep the stands and the field, lose most of the sky
rgb = rgb[top:top + crop_h]
lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
hue, sat, val = hsv(rgb)
hd = np.minimum(np.abs(hue - 16), 360 - np.abs(hue - 16))
orange = np.clip((sat - 0.25) / 0.3, 0, 1) * np.clip((val - 0.2) / 0.25, 0, 1) * np.clip(1 - hd / 26, 0, 1)
orange = np.clip(ndi.gaussian_filter(orange, 5) * 2.6, 0, 1)      # the sea, not single people
ink = 1 - local_contrast(lum, 40, 0.8)
ink = np.clip((ink - 0.12) / 0.8, 0, 1) ** 1.1
ink = ink * (1 - 0.55 * orange)               # where the orange plate prints, less navy
save(screen(ink, 10, 45), "stadium-ink.png")
save(screen(np.clip(orange * 0.95, 0, 1), 10, 15), "stadium-orange.png")

# --- 外野那群人 flag: one ink, red channel separates black lettering from orange cloth
flag = load(repo / "static/textures/flag-color.jpg", 760)
sil = Image.open(repo / "static/textures/flag-halftone.png").convert("RGBA").getchannel("A")
sil = np.asarray(sil.resize((flag.shape[1], flag.shape[0]), Image.LANCZOS), np.float32) / 255.0
sil = np.clip(ndi.gaussian_filter((ndi.binary_closing(sil > 0.2, iterations=6)).astype(np.float32), 2.5) * 1.6, 0, 1)
fval = flag.max(-1)
fink = np.clip((0.5 - fval) / 0.3, 0, 1)
fink = np.maximum(fink, 0.16)                  # cloth carries a light tint so its shape reads
save(screen(fink, 6, 45) * sil, "flag-ink.png")

# --- 萊恩 Ryan emblem: 56 CSS px tall -> 2x, two plates, cell 4 px = 2 CSS px
ry = Image.open(repo / "assets/media/ryan-head.png").convert("RGBA")
ry = ry.crop(ry.getbbox())
Wr = 180
ry = ry.resize((Wr, round(ry.height * Wr / ry.width)), Image.LANCZOS)
arr = np.asarray(ry, np.float32) / 255.0
rgb, alpha = arr[..., :3], arr[..., 3]
lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
hue, sat, val = hsv(rgb)
line = np.clip((0.42 - lum) / 0.2, 0, 1)                         # outline, cap, eyes
hue_ok = np.clip(1 - np.abs(hue - 30) / 30, 0, 1) * (1 - line)
mane = np.clip((sat - 0.55) / 0.2, 0, 1) * hue_ok
face = np.clip((sat - 0.12) / 0.2, 0, 1) * hue_ok * (1 - mane)
warm = mane + face * 0.24
pink = np.clip(1 - np.abs(((hue + 30) % 360) - 30) / 25, 0, 1) * np.clip((sat - .2) / .3, 0, 1)
warm = np.maximum(warm, pink * 0.8)
save(line * alpha, "ryan-ink.png")                                # solids print solid
save(screen(np.clip(warm * 1.05, 0, 1), 4.2, 15) * alpha, "ryan-orange.png")
print("ryan size", ry.size)

# ---------------------------------------------------------------- night plates
# On dark paper the ink is light, so a plate must carry the image's LIGHT (positive),
# not its darkness, or the photo prints as a negative.
def thr_save(alpha, name):
    save((alpha > 0.5).astype(np.float32), name)

rgb = load(repo / "static/textures/stadium-g2-color.jpg", 1920)[top:top + crop_h]
lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
lite = np.clip((local_contrast(lum, 40, 0.8) - 0.1) / 0.85, 0, 1) ** 1.2
lite = lite * (1 - 0.6 * orange)
thr_save(screen(lite, 10, 45), "stadium-ink-night.png")

flag = load(repo / "static/textures/flag-color.jpg", 760)
fval = flag.max(-1)
flite = np.clip((fval - 0.3) / 0.45, 0, 1) * 0.85
thr_save(screen(flite, 6, 45) * sil, "flag-ink-night.png")

arr = np.asarray(ry, np.float32) / 255.0
rgb, alpha = arr[..., :3], arr[..., 3]
lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
face_light = np.clip((lum - 0.55) / 0.3, 0, 1) * (1 - mane) * (1 - line)
save(screen(np.clip(face_light * 0.75 + (1 - line) * 0.0, 0, 1), 4.2, 45) * alpha, "ryan-ink-night.png")

# ---------------------------------------------------------------- page images
# Featured images of pages, printed in the same press. Plates live in static/textures/pages/
# (content/ is never edited). Name: <section>-<bundle>-ink.png / -ink-night.png
(out / "pages").mkdir(exist_ok=True)
for section, bundle, fname in [("project", "notisummary", "featured.png")]:
    im = load(repo / "content" / section / bundle / fname, 1440)
    lum = im @ np.array([0.299, 0.587, 0.114], np.float32)
    lum = local_contrast(lum, 30, 0.5)
    thr_save(screen(np.clip((1 - lum) * 0.95, 0, 1), 7, 45), f"pages/{section}-{bundle}-ink.png")
    thr_save(screen(np.clip(lum * 0.95, 0, 1), 7, 45), f"pages/{section}-{bundle}-ink-night.png")
