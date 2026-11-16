"""WOFF2 subsets for the 2026-11 redesign (plan v2, 3.2).

python fonts.py <repo> <dl>
<dl> holds the downloaded sources (see static/fonts/README.txt):
  mc/ManufacturingConsent-Regular.ttf  ultra/Ultra-Regular.ttf  franklin/LibreFranklin.ttf
  baskerville/LibreBaskerville.ttf  baskerville/LibreBaskerville-Italic.ttf  fell/IMFePIit28P.ttf
Needs fontTools + brotli.
"""
import sys, pathlib
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.varLib import instancer

repo, dl = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out = repo / "static/fonts"

def rng(a, b): return list(range(a, b + 1))
BASIC = rng(0x20, 0x7E)
LATIN1_PUNCT = rng(0xA0, 0xBF) + [0xD7, 0xF7]
# Typographic quotes, dashes, ellipsis and bullets: the titles and labels use them (“ ” ’ – — …).
GEN_PUNCT = rng(0x2010, 0x2027) + [0x2032, 0x2033, 0x2039, 0x203A, 0x20AC, 0x2122]
LABEL = BASIC + LATIN1_PUNCT + GEN_PUNCT
# Reading text: the full Latin range Google Fonts serves as "latin".
LATIN = rng(0x00, 0xFF) + [0x131, 0x152, 0x153, 0x2BB, 0x2BC, 0x2C6, 0x2DA, 0x2DC, 0x304, 0x308, 0x329] \
    + rng(0x2000, 0x206F) + [0x20AC, 0x2122, 0x2191, 0x2193, 0x2212, 0x2215, 0xFEFF, 0xFFFD]

MOTTO = "I solemnly swear that I am up to no good." + "Mischief managed." + "not"
NAMEPLATE = "The Usually Daily Chronicle"

def rename(f, family):
    """Libre Baskerville's licence reserves its name, so a modified (subset) copy gets a new one."""
    style = f["name"].getDebugName(2) or "Regular"
    for rec in list(f["name"].names):
        if rec.nameID in (1, 16): rec.string = family
        elif rec.nameID == 4: rec.string = f"{family} {style}"
        elif rec.nameID == 6: rec.string = f"{family}-{style}".replace(" ", "")
        elif rec.nameID == 3: rec.string = f"{family}-{style};subset"

def make(src, name, unicodes=None, text=None, wght=None, family=None):
    f = TTFont(src)
    if wght is not None and "fvar" in f:
        f = instancer.instantiateVariableFont(f, wght)
    if family: rename(f, family)
    o = subset.Options(); o.flavor = "woff2"; o.layout_features = ["kern", "liga", "clig", "calt", "ccmp", "locl", "mark", "mkmk"]
    o.name_IDs = ["*"]; o.notdef_outline = True
    s = subset.Subsetter(o)
    if text: s.populate(text=text)
    else: s.populate(unicodes=unicodes)
    s.subset(f)
    f.flavor = "woff2"; f.save(out / name)
    cmap = f.getBestCmap()
    want = set(map(ord, text)) if text else set(unicodes)
    missing = "".join(chr(c) for c in sorted(want) if c not in cmap and chr(c).strip() and not (0x2000 <= c <= 0x206F and c not in GEN_PUNCT))
    print(f"{name:34} {(out / name).stat().st_size / 1024:6.1f} KB  missing: {missing or 'none'}")

make(dl / "mc/ManufacturingConsent-Regular.ttf", "udc-nameplate.woff2", text=NAMEPLATE)
make(dl / "ultra/Ultra-Regular.ttf", "udc-ultra.woff2", unicodes=LABEL)
make(dl / "franklin/LibreFranklin.ttf", "udc-franklin-500.woff2", unicodes=LABEL, wght={"wght": 500})
make(dl / "franklin/LibreFranklin.ttf", "udc-franklin-700.woff2", unicodes=LABEL, wght={"wght": 700})
make(dl / "baskerville/LibreBaskerville.ttf", "udc-baskerville-400.woff2", unicodes=LATIN, wght={"wght": 400}, family="UDC Text")
make(dl / "baskerville/LibreBaskerville.ttf", "udc-baskerville-700.woff2", unicodes=LATIN, wght={"wght": 700}, family="UDC Text")
make(dl / "baskerville/LibreBaskerville-Italic.ttf", "udc-baskerville-italic.woff2", unicodes=LATIN, wght={"wght": 400}, family="UDC Text")
make(dl / "fell/IMFePIit28P.ttf", "udc-motto.woff2", text=MOTTO)
