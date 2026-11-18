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
Not shipped: 玉ねぎ楷書「激」 (玉点堂). Its licence allows use as an image but forbids redistributing the
  font file, so only the rendered lettering is in static/textures/.

Removed 2026-11-16 with the variations: Metropolitan Line, Newsreader, Dela Gothic One, Hammersmith One,
Source Serif 4, Iansui, Fraunces, Chiron Sung HK, and the spec-* specimen subsets.

Earlier entries
===============
The October 2026 font sets (Archivo, Source Sans 3, Noto Sans TC, Noto Serif TC 600–700 Google subsets,
Barlow Condensed, Lobster Two, Anybody, Mantou Sans as "UDC Field TC", Fraunces, Chiron Sung HK) were
removed on 2026-11-16 because nothing loads them; recoverable from git history (commit 178802a).
