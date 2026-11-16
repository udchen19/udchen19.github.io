"""Paper-only contrast check (plan v2, 3.4).

python paper_contrast.py <page url> <out dir> [light|dark]

Captures the full page at 1280 (1x) and 375 (2x) with every element hidden except the sheet
(paper, creases, edges, press), then computes the relative luminance of every pixel inside the
content column. Light edition pass: no pixel below 0.423, the level where --udc-ink text keeps
7:1 and --udc-ink-2 keeps 4.5:1. Dark edition pass: no pixel above the mirrored ceiling.
The content column is computed from the same values as .udc-wrap in custom.css.
"""
import sys, json, pathlib, subprocess, os
import numpy as np
from PIL import Image

url, out = sys.argv[1], pathlib.Path(sys.argv[2]); theme = sys.argv[3] if len(sys.argv) > 3 else "light"
out.mkdir(parents=True, exist_ok=True)
here = pathlib.Path(__file__).parent

def lin(c):
    c = np.asarray(c, np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

def L(rgb):
    c = lin(rgb)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]

def ratio(a, b):
    a, b = max(a, b), min(a, b)
    return (a + 0.05) / (b + 0.05)

INK, INK2 = {"light": ("#1B2436", "#3A4252"), "dark": ("#C9C6BA", "#8F96A3")}[theme]
hexrgb = lambda h: [int(h[i:i + 2], 16) for i in (1, 3, 5)]
Lk, Lk2 = L(hexrgb(INK)), L(hexrgb(INK2))
if theme == "light":
    floor = max(7 * (Lk + 0.05) - 0.05, 4.5 * (Lk2 + 0.05) - 0.05)       # lowest allowed paper L
else:
    floor = min((Lk + 0.05) / 7 - 0.05, (Lk2 + 0.05) / 4.5 - 0.05)       # highest allowed paper L

HIDE = ("document.head.insertAdjacentHTML('beforeend','<style>body *{visibility:hidden!important}"
        ".udc-sheet-layer,.udc-sheet-layer *{visibility:visible!important}</style>');"
        "new Promise(r=>setTimeout(r,600))")
jobs = []
for w, mobile in ((1280, False), (375, True)):
    jobs.append({"url": url, "out": str(out / f"paper-{theme}-{w}.png"), "width": w, "mobile": mobile,
                 "theme": theme, "eval": HIDE, "wait": 2500})
jf = out / "paper-jobs.json"; jf.write_text(json.dumps(jobs))
subprocess.run(["node", str(here / "shoot.mjs"), str(jf)], check=True, env={**os.environ})
jf.unlink()

def column(W):
    """Content column (as .udc-wrap) and the top edge's depth, in CSS px."""
    l, r, g, t = (22, 32, 18, 12) if W >= 641 else (9, 19, 12, 6)
    wrap = min(1200, W - l - r - 2 * g)
    left = (W - wrap) / 2 + (l - r) / 2
    return left, left + wrap, t

ok = True
for w in (1280, 375):
    im = np.asarray(Image.open(out / f"paper-{theme}-{w}.png").convert("RGB"))
    scale = im.shape[1] / w
    x0, x1, top = column(w)
    sub = im[int(top * scale):, int(np.ceil(x0 * scale)):int(x1 * scale)]
    lum = L(sub.reshape(-1, 3)).reshape(sub.shape[:2])
    bad = (lum < floor) if theme == "light" else (lum > floor)
    pct = bad.mean() * 100
    worst = lum.min() if theme == "light" else lum.max()
    print(f"{theme} {w}px: column x {x0:.0f}–{x1:.0f}, y {top}–end CSS px, {lum.size} pixels, "
          f"luminance min {lum.min():.3f} median {np.median(lum):.3f} max {lum.max():.3f}; "
          f"limit {floor:.3f}; beyond limit {pct:.3f}% ({int(bad.sum())} px); "
          f"ink on the worst pixel {ratio(worst, Lk):.2f}:1, ink-2 {ratio(worst, Lk2):.2f}:1")
    if bad.any():
        ok = False
        ys, xs = np.nonzero(bad)
        print(f"   first failing pixels (CSS px): {[(round(x / scale + x0), round(y / scale + top)) for y, x in list(zip(ys, xs))[:6]]}")
print("PASS" if ok else "FAIL")
