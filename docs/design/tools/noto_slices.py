"""Noto Serif TC as static unicode-range slices (the same slicing the Google Fonts TC CSS uses).

python noto_slices.py <repo> <NotoSerifTC variable .ttf> <weight> [<weight> ...]
Writes static/fonts/noto-serif-tc-<W>-N.woff2 and assets/css/udc-type-tc-<W>.part (the @font-face
blocks, to paste into assets/css/udc-type.css). The ranges are read from the existing weight-400
blocks in udc-type.css, so every weight is cut the same way. A page downloads only the slices its
characters need.
"""
import sys, re, glob, os, pathlib
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.varLib import instancer

repo = pathlib.Path(sys.argv[1]); src = sys.argv[2]; weights = [int(w) for w in sys.argv[3:]]
css = (repo / "assets/css/udc-type.css").read_text()
ranges = re.findall(r"font-family: 'Noto Serif TC';\s*font-style: normal;\s*font-weight: 400;.*?unicode-range: ([^;]+);", css, re.S)
assert ranges, "no Noto Serif TC 400 blocks found in udc-type.css"

def cps(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.strip().replace("U+", "").partition("-")
        out += range(int(a, 16), int(b or a, 16) + 1)
    return out

base = TTFont(src); cmap = base.getBestCmap(); base.close()
for W in weights:
    for old in glob.glob(str(repo / f"static/fonts/noto-serif-tc-{W}-*.woff2")): os.remove(old)
    blocks, n = [], 0
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
    (repo / f"assets/css/udc-type-tc-{W}.part").write_text("\n".join(blocks) + "\n")
    print(W, n, "slices")
