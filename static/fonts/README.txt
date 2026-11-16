Self-hosted fonts for udchen.tw

Redesign 2026-11 (branch redesign/2026-11-variations)
=====================================================
All files below were downloaded on 2026-11-11, checked for glyph coverage against the
exact fixed strings (table: data/specimen_glyphs.json, shown on /specimen/), then
subset and converted to WOFF2 with fontTools 4.55. All are SIL Open Font License 1.1.
None of the licence files declares a Reserved Font Name except Hammersmith One;
subsets of that font, and every specimen-only subset, ship under new names anyway.

Metropolitan Line (= Railway Sans) — Justin Howes, Greg Fleming, Alexei Vanyashin
  Source: https://github.com/googlefonts/metropolitan-line (fonts/ttf/MetropolitanLine-Regular.ttf)
  The googlefonts/railway-sans repository now redirects here; the README states it is a
  derivative of Railway Sans, drawn from Johnston's 1916 proofs, not from TfL's New Johnston.
  One weight only (Regular): font-synthesis is off, no faux bold.
  File: udc-metro.woff2 (Latin subset, 19 KB). Licence: MetropolitanLine-OFL.txt.

Newsreader — Production Type
  Source: https://github.com/google/fonts/tree/main/ofl/newsreader (variable opsz 6–72, wght 200–800)
  Latin subset; optical size pinned at 16 and weight limited with fontTools.varLib.instancer:
  roman keeps wght 400–700 (variable), italic is a static 400 (the only italic used).
  Files: udc-newsreader.woff2 (41 KB), udc-newsreader-italic.woff2 (25 KB). Licence: Newsreader-OFL.txt.

Dela Gothic One — syakuzen (Dela Gothic Project)
  Source: https://github.com/google/fonts/tree/main/ofl/delagothicone
  Latin subset for type theme Y. File: udc-dela-latin.woff2 (16 KB). Licence: DelaGothicOne-OFL.txt.

UDC Brush TC — subset of 莫大毛筆 Bakudai Bold v1.48 (max32002), based on 衡山毛筆フォント
  by 青柳衡山. Source: https://github.com/max32002/bakudaifont (tw/Bakudai-Bold.ttf)
  Included text: 陳威達 only. Renamed "UDC Brush TC". File: udc-brush-tc.woff2 (5 KB).
  Licence: Bakudai-OFL.txt (the repository's SIL_Open_Font_License_1.1.txt).

UDC Field TC — existing subset of Mantou Sans (see the earlier entry below); used by
  type theme Y for 陳威達. Glyphs 陳威達 confirmed present.

Specimen-only comparison faces (removed with the specimen page, plan 6.3)
  UDC Spec Hammer — Hammersmith One, Sorkin Type (RFN "Hammersmith", hence renamed).
    https://github.com/google/fonts/tree/main/ofl/hammersmithone · spec-hammer.woff2 · HammersmithOne-OFL.txt
  UDC Spec Source Serif — Source Serif 4, Adobe. https://github.com/google/fonts/tree/main/ofl/sourceserif4
    spec-sourceserif.woff2 · SourceSerif4-OFL.txt
  UDC Spec Noto Serif TC — Noto Serif TC (variable), Google. https://github.com/google/fonts/tree/main/ofl/notoseriftc
    Subset to the opening of content/post/books-summer-2021 + 陳威達片次也北公花突化名心.
    spec-notoserif-tc.woff2 · notoseriftc-OFL.txt
  UDC Spec Iansui — 芫荽 Iansui v1.020, ButTaiwan. https://github.com/ButTaiwan/iansui
    Same subset text. spec-iansui.woff2 · Iansui-OFL.txt
  Fraunces (earlier baseline, below) is declared only in assets/css/udc-specimen-fonts.css.

Noto Serif TC — Google (Source Han Serif TC). Chosen on the specimen 2026-11-11 as the 繁體中文
  reading face (Taiwan-standard forms). Source: google/fonts ofl/notoseriftc (NotoSerifTC[wght].ttf).
  Cut into 111 unicode-range slices (same slicing as the Google Fonts TC slices) and instanced to
  static 400 and 700: noto-serif-tc-400-N.woff2 / noto-serif-tc-700-N.woff2 (docs/design/tools/
  noto_slices.py). A page downloads only the slices its characters need. Licence: notoseriftc-OFL.txt.
Chiron Sung HK is no longer loaded by the site; it stays only as the specimen baseline
  (assets/css/udc-specimen-fonts.css) until the removal plan.

Earlier entries
===============

Active type system (2026-10-20)
------------------------------
Fraunces — Undercase Type / Phaedra Charles and Flavia Zimbardi
https://fraunces.undercase.xyz/
https://github.com/google/fonts/tree/main/ofl/fraunces
Roman and italic, weight 400–750 with optical sizing 9–144.
Files: fraunces-*.woff2. License: OFL-fraunces.txt.

Chiron Sung HK (昭源宋體) — Tamcy
https://github.com/chiron-fonts/chiron-sung-hk
https://github.com/google/fonts/tree/main/ofl/chironsunghk
Traditional Chinese reading and display type, weight 400–700.
Files: chiron-sung-*.woff2. License: OFL-chironsunghk.txt.

Retrieved from the official Google Fonts CSS API on 2026-10-20.
The supplied unicode subsets were losslessly converted to WOFF2 with
fontTools; outlines, naming and variable axes were not altered.
assets/css/udc-type.css retains the distributed unicode ranges so browsers
request only the subsets needed on each page. Fonts are served locally.
The same families cover navigation, headings and body text throughout the site.

Previous display fonts (retained, no longer loaded)
--------------------------------
Anybody — Tyler Finck / Etcetera Type Company
https://github.com/Etcetera-Type-Co/Anybody
Downloaded roman and italic variable fonts from:
https://github.com/google/fonts/tree/main/ofl/anybody
anybody-roman.woff2 and anybody-italic.woff2 retain the weight/width axes,
with Latin and general punctuation subsets. License: Anybody-OFL.txt.

UDC Field TC — a renamed, display-only subset of Mantou Sans:
https://github.com/mant0u0/MantouSans
Source: Font/MantouSans-Regular.ttf, downloaded 2026-10-20.
Based on Artakana's Dela Gothic One; see MantouSans-OFL.txt.
Subsetting and WOFF2 conversion use fontTools. The modified font name is
"UDC Field TC", respecting the original font's reserved names.
Included text: 陳威達近況精選研究與實作關於文章履歷興趣出版品
This earlier display system used Noto Sans TC as its fallback.
These display faces are no longer declared in the active stylesheet.

Reading fonts and earlier display assets
---------------------------------------
Source Sans 3 and Noto Sans TC are retained but no longer loaded.
Earlier display files below are retained but display.css/accent.css are
no longer loaded by the site.

Archivo — Omnibus-Type: https://github.com/Omnibus-Type/Archivo
Source Sans 3 — Adobe: https://github.com/adobe-fonts/source-sans
Noto Sans TC and Noto Serif TC — https://fonts.google.com/noto

Downloaded from the official Google Fonts CSS API on 2026-10-19.
The WOFF2 files are unmodified unicode subsets distributed by Google Fonts.
fonts.css retains the original unicode ranges and variable weight ranges.
Each visitor loads only the character subsets needed by the page.
The corresponding SIL Open Font License files are included alongside the fonts.

Families/ranges:
Archivo 600–800
Source Sans 3 400–700 (normal and italic)
Noto Sans TC 400–700
Noto Serif TC 600–700

Barlow Condensed — Jeremy Tribby: https://github.com/jpt/barlow
Display type: 600/700/800 upright, 700/800 italic. Self-hosted Google Fonts subsets in display.css; SIL OFL included.

Lobster Two — Pablo Impallari: https://github.com/impallari/The-Lobster-Font
Log heading only: 700 italic, self-hosted Latin subset in accent.css; SIL OFL included.
Noto Sans TC 900 — a Google Fonts text subset for the Chinese name and homepage
section headings, exposed as "UDC Display TC" to keep the body type independent.
Both accent families were downloaded from the official Google Fonts CSS API on
2026-10-19. Font binaries are unmodified; the Noto Sans TC license already included
in this directory also applies to its display subset.
