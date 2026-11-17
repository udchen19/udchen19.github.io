"""Halftone plates for the udchen.tw redesign (plan v2, 3.5 and Appendix B).

python halftone.py <repo> <plate> [<plate> ...]
plates: ryan icon portrait stadium flag jingu hogwarts thames pages figure404 night

Every output is a 1-bit mask (white + alpha, or opaque/transparent palette PNG) coloured by CSS
mask-image, so the light and night editions share one file where possible. Inks come from tokens.
Deterministic.
"""
import sys, pathlib, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

repo = pathlib.Path(sys.argv[1]); out = repo / "static/textures"

def dither(white, threshold_map):
    """ImageMagick's ordered dither (the plan's recipes, Appendix B) on a 0..1 array where 1 = paper.
    Returns 0/1 (1 = paper). threshold_map e.g. "h6x6a", "h8x8a", "h8x8o"."""
    with tempfile.TemporaryDirectory() as t:
        src, dst = pathlib.Path(t, "in.png"), pathlib.Path(t, "out.png")
        Image.fromarray((np.clip(white, 0, 1) * 255).round().astype(np.uint8), "L").save(src)
        subprocess.run(["magick", str(src), "-ordered-dither", threshold_map, str(dst)], check=True)
        return (np.asarray(Image.open(dst).convert("L"), np.float32) > 127).astype(np.float32)

def screen(cover, threshold_map):
    """Ink dots (1 = ink) for coverage 0..1."""
    return 1 - dither(1 - cover, threshold_map)

def save_mask(a, name):
    """1-bit mask: palette PNG, index 1 = ink (opaque white), index 0 = transparent."""
    im = Image.fromarray((np.clip(a, 0, 1) > 0.5).astype(np.uint8), "P")
    im.putpalette([0, 0, 0, 255, 255, 255] + [0] * 762)
    im.save(out / name, optimize=True, transparency=0)
    print(f"{name:30} {im.size} {(out / name).stat().st_size / 1024:.1f} KB")

def hsv(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn + 1e-6
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return hue, d / (mx + 1e-6), mx

def ryan():
    """Single ink; depth by dots (plan 3.5): outline solid, cap densest, mane medium, face lightest.
    Display 84 CSS px wide on the home page; mask at 4x (336 px), dot cell 8 px = 2 CSS px."""
    im = Image.open(repo / "assets/media/ryan-head.png").convert("RGBA")
    im = im.crop(im.getbbox())
    W = 336; H = round(im.height * W / im.width)
    # Segment at the source resolution (lines are ~8 px there), then shrink each region.
    arr = np.asarray(im, np.float32) / 255.0
    rgb, alpha = arr[..., :3], arr[..., 3] > 0.5
    hue, sat, val = hsv(rgb)
    black = (val < 0.3) & alpha
    capbody = ndi.binary_opening(black, structure=np.ones((31, 31)))   # the one large black area
    lab, n = ndi.label(capbody)
    sizes = ndi.sum(capbody, lab, range(1, n + 1))
    cap = (lab == (int(np.argmax(sizes)) + 1)) if n else np.zeros_like(black)
    cap = ndi.binary_dilation(cap, iterations=4) & black
    hull = ndi.binary_fill_holes(ndi.binary_dilation(cap, iterations=12))
    logo = (val > 0.8) & (sat < 0.2) & hull & alpha
    orange = (sat > 0.55) & (hue > 8) & (hue < 40) & alpha & ~black
    brim = orange & (val < 0.88) & ndi.binary_dilation(hull, iterations=40)   # darker orange under the cap
    mane = orange & ~brim
    face = alpha & ~black & ~orange & ~logo
    line = black & ~cap
    def shrink(m):
        return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BOX), np.float32) / 255.0
    cover = np.zeros((H, W), np.float32)
    for m, c in ((face, 0.14), (mane, 0.42), (brim, 0.62), (cap, 0.82)):
        sm = shrink(m); cover = np.where(sm > 0.5, c, cover)
    ink = np.maximum(screen(cover, "h8x8a"), (shrink(line) > 0.3).astype(np.float32))
    ink[shrink(logo) > 0.5] = 0
    a_small = shrink(alpha) > 0.5
    print("ryan", (W, H), {k: int(v.sum()) for k, v in dict(cap=cap, brim=brim, mane=mane, face=face, line=line, logo=logo).items()})
    alpha = a_small
    save_mask(ink * alpha, "ryan-ink.png")

def icon():
    """Tab icon (UD, 2026-11-17: Ryan replaces 達): the printed Ryan of ryan-ink.png in the orange, on the
    paper rounded square the 達 icon used, so it holds in light and dark tab bars. Blox reads
    assets/media/icon.png and makes the favicon and the 180 px apple-touch icon from it. Run after ryan."""
    N = 512; paper, orange = (0xE2, 0xDD, 0xD1, 255), (0xB5, 0x50, 0x1F, 255)
    m = Image.open(out / "ryan-ink.png").convert("RGBA").getchannel("A")
    k = N * 0.86 / max(m.size); m = m.resize((round(m.width * k), round(m.height * k)), Image.LANCZOS)
    im = Image.new("RGBA", (N, N), paper); im.paste(Image.new("RGBA", m.size, orange), ((N - m.width) // 2, (N - m.height) // 2 + 8), m)
    corner = Image.new("L", (N, N), 0); ImageDraw.Draw(corner).rounded_rectangle((0, 0, N - 1, N - 1), radius=N * 40 // 256, fill=255)
    im.putalpha(corner)
    dest = repo / "assets/media/icon.png"; im.save(dest, optimize=True)
    print(f"icon.png {im.size} {dest.stat().st_size / 1024:.1f} KB")

def portrait():
    """Plan 3.5 and Appendix B: full colour, ordered-dither halftone, dot cell 1.5 CSS px at the
    display size (282 px wide -> master 1128 px, cell 6 px), saturation 45% of the source (UD, 2026-11-16;
    70% read too colourful: each dot is a pure screen colour), on a paper
    tint; no frame. [P] The selfie's cut-off left and bottom edges dissolve into smaller dots over
    24 CSS px (96 px here) instead of ending in a straight line."""
    src = repo / "docs/design/v2/sources/portrait-raised-fist.png"
    im = Image.open(src).convert("RGBA")
    W = 1128; H = round(im.height * W / im.width)
    im = im.resize((W, H), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255.0
    rgb, alpha = a[..., :3], a[..., 3:]
    # Appendix B: flatten on a paper tint, saturation 45%, unsharp, ordered dither per
    # channel at 2 levels (h6x6a), multiplied onto a lighter paper tint.
    with tempfile.TemporaryDirectory() as t:
        dst = pathlib.Path(t, "p.png")
        subprocess.run(["magick", str(src), "-resize", f"{W}x", "-background", "#E6E1D5", "-flatten", "-alpha", "off",
                        "-modulate", "102,45,100", "-unsharp", "0x1.5+0.9+0", "-ordered-dither", "h6x6a,2",
                        "(", "-size", f"{W}x{H}", "xc:#EBE6DA", ")", "-compose", "Multiply", "-composite", str(dst)], check=True)
        out_rgb = np.asarray(Image.open(dst).convert("RGB"), np.float32)[:H, :W] / 255
    # Edge dissolve where the photo itself is cut (alpha reaches the left and bottom borders).
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ramp = np.clip(xx / 96, 0, 1) * np.clip((H - 1 - yy) / 96, 0, 1)
    keep = screen(ramp, "h6x6a")
    a1 = (alpha[..., 0] > 0.5).astype(np.float32) * np.where(ramp < 1, keep, 1)
    print("portrait", (W, H), "left cut rows", int((alpha[:, 0, 0] > .5).sum()), "bottom cut cols", int((alpha[-1, :, 0] > .5).sum()))
    pal_im = Image.fromarray((np.clip(out_rgb, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")
    pal_im.putalpha(Image.fromarray((a1 * 255).astype(np.uint8)))
    pal_im.save(out / "portrait.webp", lossless=True, method=6)
    for n in ("portrait.webp",):
        print(f"{n:30} {(out / n).stat().st_size / 1024:.1f} KB")

def magick(*args):
    subprocess.run(["magick", *map(str, args)], check=True)

def load_gray(path):
    return np.asarray(Image.open(path).convert("L"), np.float32) / 255.0

def save_gray(a, path):
    Image.fromarray((np.clip(a, 0, 1) * 255).round().astype(np.uint8), "L").save(path)

def bottom_ramp(h, frac):
    """0 above the last frac of the height -> 1 at the bottom edge: the image's dots grow into the solid
    ink strip under the footer (UD, 2026-11-16: the image is not covered; a short fade into the strip)."""
    return np.clip((np.arange(h, dtype=np.float32) - h * (1 - frac)) / (h * frac), 0, 1)[:, None]

BOTTOM = 0.08

# Footer plates (home and section footers, day and night): master size and dot grid. The dot in CSS px
# is CELL * (footer width) / FW; the footer spans the window. UD, 2026-11-16, after a big screen: 4 px at
# 1280 (6 px at 1920), was 5 px (2048x819).
FW, FH, CELL = 2560, 1024, "h8x8"

# The top fade (UD, 2026-11-17: it met the paper too abruptly). An ordered dither turns a smooth vertical
# ramp into ruled lines: every cell switches on its first dot at the same row, so the picture began with
# a hard line of tiny dots. The fade is therefore ragged: its position is pushed up and down per dot cell
# (fine noise) and in a slow wave (coarse noise), so dots start at different heights, like ink thinning
# out on rough paper; then eased (smoothstep) over a taller band. Fixed seed: same plate on every run.
TOP, RAGGED = 0.3, 0.3

def top_fade(h, frac=TOP, w=None):
    """0 at the top edge -> 1 below frac of the height: the footer fades up into the paper (4.6).
    (h, w) when w is given; the ragged part needs the width."""
    y = np.arange(h, dtype=np.float32)[:, None] / (h * frac)
    if w is None:
        x = np.clip(y, 0, 1)
    else:
        rng = np.random.default_rng(7)
        def noise(sigma):
            n = ndi.gaussian_filter(rng.standard_normal((h, w)).astype(np.float32), sigma)
            return n / (n.std() + 1e-6)
        n = np.clip(0.7 * noise(4) + 0.3 * noise(90), -2, 2) / 2          # about -1..1
        x = np.clip(y * (1 + RAGGED) - RAGGED + RAGGED * n, 0, 1)            # 0 along the whole top edge
    return x * x * (3 - 2 * x)

def sky_pad(src, pad, t):
    """The source with `pad` px of its own sky added above, so a subject near the top edge sits below
    the taller fade. Each column continues its top rows' colour, blurred sideways; the fade covers it."""
    im = np.asarray(Image.open(src).convert("RGB"), np.float32)
    top = ndi.gaussian_filter1d(im[:24].mean(0), 40, axis=0)
    sky = np.repeat(top[None], pad, 0)
    blend = np.linspace(0, 1, 24, dtype=np.float32)[:, None, None]
    im[:24] = sky[-1] * (1 - blend) + im[:24] * blend           # no seam where the sky meets the photo
    dest = pathlib.Path(t) / f"pad-{pathlib.Path(src).stem}.png"
    Image.fromarray(np.vstack([sky, im]).clip(0, 255).astype(np.uint8)).save(dest)
    return dest

def stadium(cell=None, W=None, H=None):
    """Home footer (plan 3.5, Appendix B). Same master and cell as the section footers (FW, FH, CELL;
    Checkpoint B chose a shared cell; 4 px at 1280 since 2026-11-16).
    Navy + orange; orange only on the stands, graded by shirt saturation. [P] The top (TOP) is a
    halftone fade (dots shrink to nothing), not an alpha fade."""
    cell, W, H = cell or CELL, W or FW, H or FH
    src = repo / "static/textures/stadium-g2-color.jpg"
    tag = ""
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        magick(src, "-crop", "800x320+0+125", "+repage", t / "crop.png")
        magick("-size", "800x320", "xc:white", "-fill", "black", "-draw", "ellipse 397,190 240,98 0,360", "-blur", "0x4", t / "field.png")
        magick(t / "crop.png", "-fx", "(u.r>0.30 && (u.r-u.g)>0.08 && (u.r-u.b)>0.12) ? min(1,(u.r-u.g)*4.6) : 0",
               "-colorspace", "Gray", t / "field.png", "-compose", "Multiply", "-composite", t / "or.png")
        magick(t / "crop.png", "-colorspace", "HSB", "-channel", "B", "-separate", "+channel", t / "val.png")
        magick(t / "val.png", "(", t / "or.png", "-evaluate", "Multiply", "0.8", ")", "-compose", "Screen", "-composite", t / "val2.png")
        magick(t / "val2.png", "-filter", "Lanczos", "-resize", f"{W}x{H}!", "-unsharp", "0x2+1.3+0", "-level", "4%,82%", "-gamma", "1.25", t / "valp.png")
        magick(t / "or.png", "-filter", "Lanczos", "-resize", f"{W}x{H}!", "-unsharp", "0x1.5+0.8+0", "-level", "4%,96%", t / "orp.png")
        ramp = top_fade(H, w=W)
        low = bottom_ramp(H, BOTTOM)
        save_gray((1 - (1 - load_gray(t / "valp.png")) * ramp) * (1 - low), t / "valf.png")   # paper at the top, ink at the bottom
        save_gray(load_gray(t / "orp.png") * ramp * (1 - low), t / "orf.png")
        magick(t / "valf.png", "-ordered-dither", cell + "a", "-negate", t / "ink.png")             # white = ink
        magick(t / "orf.png", "-negate", "-ordered-dither", cell + "o", "-negate", t / "orange.png")  # white = orange
        ink, orange = load_gray(t / "ink.png") > .5, load_gray(t / "orange.png") > .5
    cover = float((orange & ~ink).mean())
    print(f"stadium{tag}: orange after the navy prints over it = {cover * 100:.2f}% of the image (plan: 8-10%)")
    save_mask(ink.astype(np.float32), f"stadium-ink{tag}.png")
    save_mask(orange.astype(np.float32), f"stadium-orange{tag}.png")

def flag():
    """外野那群人 (plan 3.5, Appendix B): flat, no dots. Orange cloth, paper outline, ink lettering.
    Lettering by the red channel (r < 0.30), outline by g > 0.50 and b > 0.40; work at 300%."""
    src = repo / "static/textures/flag-color.jpg"
    im = Image.open(src).convert("RGB")
    im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    ink = ndi.binary_opening(r < 0.30, structure=ndi.generate_binary_structure(2, 1))   # Open Disk:1
    outline = (g > 0.50) & (b > 0.40)
    poly = Image.new("L", im.size, 0)
    from PIL import ImageDraw
    ImageDraw.Draw(poly).polygon([(60, 36), (750, 126), (1050, 300), (1104, 798), (735, 831), (180, 786)], fill=255)
    cloth = np.asarray(poly) > 127
    box = (60, 36, 1105, 832)                                        # the polygon's bounding box
    crop = lambda m: m[box[1]:box[3], box[0]:box[2]].astype(np.float32)
    save_mask(crop(cloth), "flag-cloth.png")
    save_mask(crop(cloth & outline & ~ink), "flag-outline.png")
    save_mask(crop(cloth & ink), "flag-ink.png")
    print("flag", (box[2] - box[0], box[3] - box[1]))

def section(name, src, crop, width=None, pad=0):
    """Section footers (plan 3.5, Appendix B): FW x FH master, CELL grid -> 4 px at 1280. The
    second ink is a tint over the mid-tones of the whole image (sky included); navy only in the
    shadows. The top is a halftone fade into the paper (TOP), as on the home footer."""
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        pre = ["-resize", f"{width}x"] if width else []
        if pad: src = sky_pad(src, pad, t)
        magick(src, *pre, "-crop", crop, "+repage", t / "crop.png")
        magick(t / "crop.png", "-colorspace", "Gray", "-filter", "Lanczos", "-resize", f"{FW}x{FH}!", "-unsharp", "0x2+1.2+0", t / "L.png")
        magick(t / "L.png", "-negate", "-level", "8%,78%", "-negate", t / "c.png")
        magick(t / "L.png", "-level", "0%,52%", "-gamma", "0.85", t / "k.png")
        ramp = top_fade(FH, w=FW)
        low = bottom_ramp(FH, BOTTOM)
        save_gray((1 - (1 - load_gray(t / "c.png")) * ramp) * (1 - low), t / "cf.png")
        save_gray((1 - (1 - load_gray(t / "k.png")) * ramp) * (1 - low), t / "kf.png")
        magick(t / "cf.png", "-ordered-dither", CELL + "o", "-negate", t / "colour.png")   # white = second ink
        magick(t / "kf.png", "-ordered-dither", CELL + "a", "-negate", t / "ink.png")      # white = navy
        ink, col = load_gray(t / "ink.png") > .5, load_gray(t / "colour.png") > .5
    print(f"{name}: navy {ink.mean()*100:.1f}%, second ink showing {(col & ~ink).mean()*100:.1f}%")
    save_mask(ink.astype(np.float32), f"footer-{name}-ink.png")
    save_mask(col.astype(np.float32), f"footer-{name}-2.png")

def pages():
    """Featured images of pages, one ink (plan 4.7): shown up to 760 CSS px wide, so a 1216 px master
    with an 8 px cell gives the 5 px dot of the section footers. Plates live in static/textures/pages/
    (content/ is never edited): <section>-<bundle>-ink.png, and -ink-night.png carrying the light."""
    (out / "pages").mkdir(exist_ok=True)
    for section, bundle, fname in [("project", "notisummary", "featured.png")]:
        src = repo / "content" / section / bundle / fname
        with tempfile.TemporaryDirectory() as t:
            t = pathlib.Path(t)
            magick(src, "-background", "white", "-flatten", "-colorspace", "Gray", "-filter", "Lanczos", "-resize", "1216x", "-unsharp", "0x1.5+0.8+0", t / "L.png")
            magick(t / "L.png", "-ordered-dither", "h8x8a", "-negate", t / "ink.png")
            magick(t / "L.png", "-negate", "-ordered-dither", "h8x8a", "-negate", t / "night.png")
            save_mask((load_gray(t / "ink.png") > .5).astype(np.float32), f"pages/{section}-{bundle}-ink.png")
            save_mask((load_gray(t / "night.png") > .5).astype(np.float32), f"pages/{section}-{bundle}-ink-night.png")

def figure404():
    """404 photo (plan 4.9): natural colour, no halftone, no grain; 1400 px tall (2x the tallest
    display). UD chose it untouched over a toned version (Checkpoint B, 2026-11-16)."""
    src = repo / "docs/design/v2/sources/404-bat.png"
    magick(src, "-resize", "x1400", "-quality", "86", "-define", "webp:alpha-quality=90", out / "404-figure.webp")
    print(f"{'404-figure.webp':30} {(out / '404-figure.webp').stat().st_size / 1024:.1f} KB")

def night():
    """Night edition plates (plan 5): light ink on dark paper must carry the image's light, or photos
    print as negatives. Same crops and cells as the day plates; top fade and bottom fade both go to
    bare (dark) paper, so the image dissolves into the dark strip under the footer."""
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        # Home stadium: highlights in light ink; the day orange plate is reused (orange reads on navy).
        src = repo / "static/textures/stadium-g2-color.jpg"; W, H = FW, FH
        magick(src, "-crop", "800x320+0+125", "+repage", "-colorspace", "HSB", "-channel", "B", "-separate", "+channel",
               "-filter", "Lanczos", "-resize", f"{W}x{H}!", "-unsharp", "0x2+1.3+0", "-level", "18%,96%", "-gamma", "0.9", t / "v.png")
        orange = load_gray(t / "v.png") * 0 + (np.asarray(Image.open(out / "stadium-orange.png").convert("RGBA"))[..., 3] > 0)
        cover = load_gray(t / "v.png") * top_fade(H, w=W) * (1 - bottom_ramp(H, BOTTOM)) * (1 - 0.85 * orange)
        save_gray(1 - cover, t / "c.png")
        magick(t / "c.png", "-ordered-dither", CELL + "a", "-negate", t / "ink.png")
        save_mask((load_gray(t / "ink.png") > .5).astype(np.float32), "stadium-ink-night.png")
        # Section footers: highlights in light ink; the second ink on the mid-tones only.
        for name, src, crop, pre in [("jingu", SRC / "jingu.webp", "2000x800+0+600", []),
                                     ("hogwarts", sky_pad(SRC / "hogwarts.jpg", HOG_PAD, t), HOG_CROP, []),
                                     ("thames", SRC / "london-night-frame02-1600.jpg", "1600x640+0+110", [])]:
            magick(src, *pre, "-crop", crop, "+repage", "-colorspace", "Gray", "-filter", "Lanczos", "-resize", f"{FW}x{FH}!", "-unsharp", "0x2+1.2+0", t / "L.png")
            L = load_gray(t / "L.png"); fade = top_fade(FH, w=FW) * (1 - bottom_ramp(FH, BOTTOM))
            if name == "thames":
                # The city at night: sky and river carry little light; the lamps print in the night orange.
                magick(src, *pre, "-crop", crop, "+repage", "-filter", "Lanczos", "-resize", f"{FW}x{FH}!", t / "rgb.png")
                rgb = np.asarray(Image.open(t / "rgb.png").convert("RGB"), np.float32) / 255
                warm = np.clip((rgb.max(-1) - 0.45) / 0.35, 0, 1) * np.clip((rgb[..., 0] - rgb[..., 2]) / 0.25, 0, 1)
                light = np.clip((L - 0.10) / 0.75, 0, 1) ** 1.2 * (1 - warm)
                second = np.clip(warm * 1.4, 0, 1)
            else:
                light = np.clip((L - 0.35) / 0.6, 0, 1) ** 1.1
                second = np.clip(1 - np.abs(L - 0.45) / 0.3, 0, 1) * 0.75
            for arr, nm, tm in ((light, "ink", CELL + "a"), (second, "2", CELL + "o")):
                save_gray(1 - arr * fade, t / "c.png")
                magick(t / "c.png", "-ordered-dither", tm, "-negate", t / "m.png")
                save_mask((load_gray(t / "m.png") > .5).astype(np.float32), f"footer-{name}-{nm}-night.png")

SRC = repo / "docs/design/v2/sources"
# Jingu and Thames crops sit higher than before (2026-11-17) so the light towers and the skyline stay below
# the fade. Hogwarts: the still has almost no sky above the spires, so its sky is extended upward (sky_pad) and
# the crop starts at the top of that; the castle sits below the fade and the lake's foot is cropped.
HOG_PAD = 150
HOG_CROP = "2000x800+0+0"
PLATES = {"jingu": lambda: section("jingu", SRC / "jingu.webp", "2000x800+0+600"),
          "hogwarts": lambda: section("hogwarts", SRC / "hogwarts.jpg", HOG_CROP, pad=HOG_PAD),
          "thames": lambda: section("thames", SRC / "london-day-frame14-1600.jpg", "1600x640+0+110"),
          "ryan": ryan, "icon": icon, "portrait": portrait, "pages": pages, "figure404": figure404, "night": night, "stadium": stadium, "flag": flag}
for p in sys.argv[2:]:
    PLATES[p]()
