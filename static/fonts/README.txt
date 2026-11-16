Self-hosted fonts for udchen.tw

Redesign 2026-11, plan v2 (branch redesign/2026-11-variations)
==============================================================
Downloaded 2026-11-16 from github.com/google/fonts (the licence file beside each font was read),
subset and converted to WOFF2 with fontTools 4.55 by docs/design/tools/fonts.py.

Manufacturing Consent (The Manufacturing Consent Project Authors; designer Fredrick Brennan)
  ofl/manufacturingconsent/ManufacturingConsent-Regular.ttf. Nameplate only: subset to the letters of
  "The Usually Daily Chronicle". udc-nameplate.woff2. SIL OFL 1.1: ManufacturingConsent-OFL.txt.
Ultra (Astigmatic) — headline, page titles, research heads, 404
  apache/ultra/Ultra-Regular.ttf. Basic Latin + Latin-1 punctuation + general punctuation.
  udc-ultra.woff2. Apache License 2.0 (not OFL): Ultra-LICENSE-Apache-2.0.txt.
Libre Franklin (The Libre Franklin Project Authors; Impallari Type) — menu, labels, dates
  ofl/librefranklin/LibreFranklin[wght].ttf, instanced to static 500 and 700, same subset as Ultra.
  udc-franklin-500.woff2, udc-franklin-700.woff2. SIL OFL 1.1: LibreFranklin-OFL.txt.
Libre Baskerville (Impallari Type) — reading text, served as "UDC Text"
  ofl/librebaskerville/LibreBaskerville[wght].ttf and -Italic[wght].ttf, instanced to 400, 700 and
  italic 400; Latin range. Its licence declares the Reserved Font Name "Libre Baskerville", so the
  modified (subset) files are renamed "UDC Text". udc-baskerville-{400,700,italic}.woff2.
  SIL OFL 1.1: LibreBaskerville-OFL.txt.
IM Fell DW Pica italic (Igino Marini) — the motto and the nameplate's "not"
  ofl/imfelldwpica/IMFePIit28P.ttf, subset to those strings. udc-motto.woff2. SIL OFL 1.1: IMFellDWPica-OFL.txt.
Noto Serif TC 900 (Google) — 繁體中文 titles
  github.com/notofonts/noto-cjk Serif/Variable/TTF/Subset/NotoSerifTC-VF.ttf, instanced to 900 and cut
  into the same 111 unicode-range slices as 400/700 (docs/design/tools/noto_slices.py):
  noto-serif-tc-900-N.woff2. SIL OFL 1.1: notoseriftc-OFL.txt.
Noto Serif TC 400/700 — 繁體中文 reading text (2026-11-11; unchanged): noto-serif-tc-{400,700}-N.woff2.
莫大毛筆 Bakudai Bold (max32002) — used only to render 衝啥 as an image (static/textures/chongsha.png);
  no font file ships. Licence: Bakudai-OFL.txt. (The earlier "UDC Brush TC" subset was removed 2026-11-16.)
Not shipped: 玉ねぎ楷書「激」 (玉点堂). Its licence allows use as an image but forbids redistributing the
  font file, so only the rendered lettering is in static/textures/.

Removed 2026-11-16 with the variations: Metropolitan Line, Newsreader, Dela Gothic One, Hammersmith One,
Source Serif 4, Iansui, Fraunces, Chiron Sung HK, and the spec-* specimen subsets.

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
