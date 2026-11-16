"""Noto Serif TC 400–700 as unicode-range slices (same slicing as the Google Fonts TC slices
already used for Chiron Sung HK in udc-type.css). Writes static/fonts/noto-serif-tc-N.woff2
and prints the @font-face blocks."""
import sys, re, pathlib
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.varLib import instancer
repo = pathlib.Path(sys.argv[1]); src = sys.argv[2]
css = (repo / "assets/css/udc-specimen-fonts.css").read_text()
ranges = re.findall(r"font-family: 'Chiron Sung HK';.*?unicode-range: ([^;]+);", css, re.S)
def cps(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.strip().replace("U+", "").partition("-")
        out += range(int(a, 16), int(b or a, 16) + 1)
    return out
base = TTFont(src); cmap = base.getBestCmap(); base.close()
blocks = []
import glob, os
for old in glob.glob(str(repo / "static/fonts/noto-serif-tc-*.woff2")): os.remove(old)
for W in (400, 700):
  n = 0
  for spec in ranges:
    want = [c for c in cps(spec) if c in cmap]
    if not want: continue
    f = TTFont(src)
    o = subset.Options(); o.flavor = None; o.layout_features = ["*"]; o.notdef_outline = True
    s = subset.Subsetter(o); s.populate(unicodes=want); s.subset(f)
    f = instancer.instantiateVariableFont(f, {"wght": W})
    f.flavor = "woff2"; name = f"noto-serif-tc-{W}-{n}.woff2"; f.save(repo / "static/fonts" / name)
    blocks.append(f"@font-face {{\n  font-family: 'Noto Serif TC';\n  font-style: normal;\n  font-weight: {W};\n  font-display: swap;\n  src: url(/fonts/{name}) format('woff2');\n  unicode-range: {spec.strip()};\n}}")
    n += 1
(repo / "assets/css/udc-type-tc.part").write_text("\n".join(blocks) + "\n")
print(len(blocks), "slices")
