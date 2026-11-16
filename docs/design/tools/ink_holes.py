"""Ink holes as textures (plan v2, 3.3; switched from live SVG filters on 2026-11-16).

python ink_holes.py <repo>

The three press strengths (display d, label m, body b) were live SVG filters on the page. In WebKit
they stalled scrolling for 0.4-1.5 s (iOS Simulator, Astra review); the same holes as a CSS mask
scroll at 50-70 ms frame gaps. This script keeps the filters as the source of truth: it renders each
filter, with the exact parameters the page used, over a solid block in headless Chrome at 2x,
thresholds the result to 1 bit and writes static/textures/ink-holes-{d,m,b}.png, shown on the page
as a 512 CSS px tile (2 image px per CSS px). What is lost: the filter's 1px edge displacement.

Needs Chrome and docs/design/tools/shoot.mjs; runs with UDC_SCRATCH (or the system temp dir).
"""
import sys, os, json, pathlib, subprocess, tempfile
import numpy as np
from PIL import Image

repo = pathlib.Path(sys.argv[1]).resolve()
out = repo / "static/textures"
TILE = 512            # CSS px; the image is 2x that
STRENGTHS = {"d": (0.29, 0.25, 0.9), "m": (0.26, 0.22, 0.7), "b": (0.22, 0.17, 0.5)}   # fine, big, k

def filt(name, fine, big, k):
    # The same filter the page used (layouts/_partials/hooks/body-end/udc.html until 2026-11-16).
    return f'''<filter id="ink-{name}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="1.15" numOctaves="3" seed="3"/><feColorMatrix type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0 1" result="fine"/>
<feTurbulence type="fractalNoise" baseFrequency="0.02 0.035" numOctaves="2" seed="8"/><feColorMatrix type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0 1" result="coarse"/>
<feComposite in="fine" in2="coarse" operator="arithmetic" k1="0" k2="1" k3="{k}" k4="{-k / 2}" result="mix"/>
<feColorMatrix in="mix" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  60 0 0 0 {-60 * fine}" result="keep1"/>
<feTurbulence type="fractalNoise" baseFrequency="0.14" numOctaves="5" seed="21" result="mid"/>
<feColorMatrix in="mid" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  60 0 0 0 {-60 * big}" result="keep2"/>
<feComposite in="SourceGraphic" in2="keep1" operator="in" result="r1"/><feComposite in="r1" in2="keep2" operator="in"/>
</filter>'''

tmp = pathlib.Path(os.environ.get("UDC_SCRATCH") or tempfile.gettempdir()) / "ink-holes"
tmp.mkdir(parents=True, exist_ok=True)
defs = "".join(filt(n, *v) for n, v in STRENGTHS.items())
jobs = []
for n in STRENGTHS:
    html = tmp / f"{n}.html"
    html.write_text(f'<!doctype html><html><body style="margin:0;background:#fff"><svg width="0" height="0" style="position:absolute"><defs>{defs}</defs></svg>'
                    f'<div id="blk" style="width:{TILE}px;height:{TILE}px;background:#000;filter:url(#ink-{n})"></div></body></html>')
    jobs.append({"url": html.as_uri(), "out": str(tmp / f"{n}.png"), "width": TILE + 40, "height": TILE + 40, "theme": "light", "selector": "#blk", "scale": 2, "js": True})
(tmp / "jobs.json").write_text(json.dumps(jobs))
subprocess.run(["node", str(repo / "docs/design/tools/shoot.mjs"), str(tmp / "jobs.json")], check=True, env={**os.environ, "UDC_SCRATCH": str(tmp)})

for n in STRENGTHS:
    g = np.asarray(Image.open(tmp / f"{n}.png").convert("L"))
    g = g[: 2 * TILE, : 2 * TILE]
    assert g.shape == (2 * TILE, 2 * TILE), g.shape
    hole = g > 128                                     # paper showing through = a hole
    grey = ((g > 20) & (g < 235)).mean()
    # Two-colour palette PNG: index 0 (the holes) is transparent, index 1 opaque. A CSS mask reads the
    # alpha channel, so ink shows where the image is opaque.
    im = Image.fromarray(np.where(hole, 0, 1).astype(np.uint8), "P")
    im.putpalette([0, 0, 0, 0, 0, 0] + [0] * 762)
    dest = out / f"ink-holes-{n}.png"
    im.save(dest, optimize=True, transparency=0)
    print(f"ink-holes-{n}.png  holes {hole.mean() * 100:.2f}%  grey before threshold {grey * 100:.2f}%  {dest.stat().st_size // 1024} KB")
