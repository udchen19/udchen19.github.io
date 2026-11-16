"""Best procedural newsprint (no scan): curved short strands + flecks + cored grain.
Same gray-centred format and display size as newsprint-fibres.png, for the specimen comparison."""
import sys, pathlib, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
out = pathlib.Path(sys.argv[1]) / "static/textures"
r = np.random.default_rng(7); W, H = 1588, 2048
dark = Image.new("L", (W, H), 0); light = Image.new("L", (W, H), 0)
dd, dl = ImageDraw.Draw(dark), ImageDraw.Draw(light)
for img, d, n, amp in ((dark, dd, 2600, 150), (light, dl, 1700, 110)):
    for _ in range(n):
        x, y = r.random(2) * (W, H); a = r.uniform(0, 2 * np.pi); L = r.gamma(2.2, 7); bend = r.normal(0, .08)
        pts = []
        for i in range(8):
            pts.append((x, y)); a += bend; x += np.cos(a) * L / 7; y += np.sin(a) * L / 7
        d.line(pts, fill=int(amp * r.uniform(.4, 1)), width=1)
    for _ in range(n // 6):
        x, y = r.random(2) * (W, H); rad = r.uniform(.6, 2.2)
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=int(amp * r.uniform(.5, 1)))
grain = ndi.gaussian_filter(r.standard_normal((H, W)).astype(np.float32), .8, mode="wrap")
grain = np.sign(grain) * np.maximum(np.abs(grain) - .25, 0) * 30
v = 128 - np.asarray(dark, np.float32) * .55 + np.asarray(light, np.float32) * .45 + grain
v = ndi.gaussian_filter(v, .5)
Image.fromarray(np.clip(v, 0, 255).astype(np.uint8), "L").save(out / "newsprint-fibres-generated.png", optimize=True)
print("ok", (out / "newsprint-fibres-generated.png").stat().st_size // 1024, "KB")
