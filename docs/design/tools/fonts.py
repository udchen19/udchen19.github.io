"""Glyph coverage check and subsetting for the udchen.tw redesign.

Run with the miniconda python (fontTools + brotli):
  python fonts.py <repo> <download-dir>
Writes subsets into <repo>/static/fonts and a coverage table into
<repo>/data/specimen_glyphs.json.
"""
import json, re, sys, pathlib
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.varLib import instancer

repo = pathlib.Path(sys.argv[1]); dl = pathlib.Path(sys.argv[2])
out = repo / "static/fonts"

# --- the exact fixed strings -------------------------------------------------
FIXED = {
    "Tagline": "Unapologetically Depends on Context",
    "Headline draft 1": "When agents talk to agents, what stays in context?",
    "DRAFT mark": "DRAFT",
    "Byline": "by Uei-Dar Chen",
    "Name (Latin)": "Uei-Dar Chen",
    "Name (繁體中文)": "陳威達",
    "Field: section names": "PUBLICATIONS UD’S LOG ABOUT PROJECT NOT FOUND",
    "Labels": "RESEARCH NEWS SELECTED WORK ALL POSTS",
    "Navigation": "Research Publications UD’s Log About CV",
    "Paper title": "“I Want It to Do More Than Deliver”: Users’ Desires for Intelligent Notification Systems",
    "Dates": "Aug–Sep 2026 · 2025.09.10 · MobileHCI 2026",
    "Keywords": "personal AI agents · contextual privacy · human–agent · agent–agent · multi-agent AI systems · intelligent smartphone notification systems · notification summaries · individual preferences · feedback · proactive, context-aware · integrate, interpret, safeguard, adapt · interviews · qualitative analysis · system building · Android prototypes",
}

def md_plain(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return s.replace("*", "").replace("&emsp;", "")

yaml_text = md_plain((repo / "data/udc.yaml").read_text())
post = (repo / "content/post/books-summer-2021/index.md").read_text().split("---", 2)[2]
post_open = md_plain(post.split("<!--more-->")[0])
latin_body = "".join(sorted(set(c for c in yaml_text if ord(c) < 0x3000)))
cjk_post = "".join(sorted(set(post_open)))

# Which strings each font must carry (role-based).
DISPLAY_LATIN = [k for k in FIXED if k != "Name (繁體中文)"]
fonts = {
    "Metropolitan Line": (dl / "metro/MetropolitanLine-Regular.ttf", DISPLAY_LATIN),
    "Hammersmith One": (dl / "hammersmith/HammersmithOne-Regular.ttf", ["Tagline", "Headline draft 1", "Paper title"]),
    "Dela Gothic One": (dl / "dela/DelaGothicOne-Regular.ttf", ["Tagline", "Headline draft 1", "DRAFT mark", "Field: section names", "Labels", "Paper title", "Keywords"]),
    "莫大毛筆 Bold": (dl / "bakudai/Bakudai-Bold.ttf", ["Name (繁體中文)"]),
    "Mantou Sans (UDC Field TC subset)": (repo / "static/fonts/udc-field-tc.woff2", ["Name (繁體中文)"]),
    "Newsreader": (dl / "newsreader/Newsreader.ttf", ["Paper title", "Dates", "Keywords", "Byline"]),
    "Source Serif 4": (dl / "sourceserif/SourceSerif4.ttf", ["Paper title", "Dates", "Keywords"]),
    "Noto Serif TC": (dl / "notoserif/NotoSerifTC.ttf", ["Name (繁體中文)"]),
    "Iansui": (dl / "iansui/Iansui-Regular.ttf", ["Name (繁體中文)"]),
}
EXTRA = {"Newsreader": ("Research text (data/udc.yaml)", latin_body),
         "Source Serif 4": ("Research text (data/udc.yaml)", latin_body),
         "Noto Serif TC": ("Post opening (books-summer-2021)", cjk_post),
         "Iansui": ("Post opening (books-summer-2021)", cjk_post)}

table = []
for name, (path, keys) in fonts.items():
    cmap = TTFont(path, lazy=True).getBestCmap()
    rows = [(k, FIXED[k]) for k in keys]
    if name in EXTRA: rows.append(EXTRA[name])
    for label, text in rows:
        missing = sorted(set(c for c in text if not c.isspace() and ord(c) not in cmap and c not in " "))
        table.append({"font": name, "string": label, "chars": len(set(text) - {" "}),
                      "missing": "".join(missing)})
        print(f"{name:36} {label:34} missing: {''.join(missing) or '—'}")
(repo / "data").mkdir(exist_ok=True)
(repo / "data/specimen_glyphs.json").write_text(json.dumps(table, ensure_ascii=False, indent=1))

# --- subsets -----------------------------------------------------------------
LATIN = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,"
         "U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")

def ranges(spec):
    u = []
    for part in spec.split(","):
        a, _, b = part.replace("U+", "").partition("-")
        u += list(range(int(a, 16), int(b or a, 16) + 1))
    return u

def rename(font, family):
    for rec in font["name"].names:
        if rec.nameID in (1, 4, 16, 18, 21):
            rec.string = family
        elif rec.nameID == 6:
            rec.string = family.replace(" ", "")
        elif rec.nameID == 3:
            rec.string = family + " subset"

def make(src, dst, unicodes=None, text=None, family=None, limits=None):
    f = TTFont(src)
    if limits:
        f = instancer.instantiateVariableFont(f, limits)
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["*"]
    opts.name_IDs = ["*"]; opts.name_languages = ["*"]; opts.notdef_outline = True
    s = subset.Subsetter(opts)
    s.populate(unicodes=unicodes or [], text=text or "")
    s.subset(f)
    if family: rename(f, family)
    f.flavor = "woff2"; f.save(out / dst)
    print(f"wrote {dst:34} {(out / dst).stat().st_size // 1024} KB")

latin = ranges(LATIN)
make(dl / "metro/MetropolitanLine-Regular.ttf", "udc-metro.woff2", unicodes=latin)
make(dl / "newsreader/Newsreader.ttf", "udc-newsreader.woff2", unicodes=latin,
     limits={"wght": (300, 700), "opsz": (6, 72)})
make(dl / "newsreader/Newsreader-Italic.ttf", "udc-newsreader-italic.woff2", unicodes=latin,
     limits={"wght": (300, 700), "opsz": (6, 72)})
make(dl / "dela/DelaGothicOne-Regular.ttf", "udc-dela-latin.woff2", unicodes=latin)
make(dl / "bakudai/Bakudai-Bold.ttf", "udc-brush-tc.woff2", text="陳威達", family="UDC Brush TC")
# Specimen-only comparison faces (removed with the specimen, plan 6.3 step 4/5).
make(dl / "hammersmith/HammersmithOne-Regular.ttf", "spec-hammer.woff2", unicodes=latin, family="UDC Spec Hammer")
make(dl / "sourceserif/SourceSerif4.ttf", "spec-sourceserif.woff2", unicodes=latin, family="UDC Spec Source Serif")
make(dl / "notoserif/NotoSerifTC.ttf", "spec-notoserif-tc.woff2", text=cjk_post + "陳威達",
     limits={"wght": (400, 700)}, family="UDC Spec Noto Serif TC")
make(dl / "iansui/Iansui-Regular.ttf", "spec-iansui.woff2", text=cjk_post + "陳威達", family="UDC Spec Iansui")
