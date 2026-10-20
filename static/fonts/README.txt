Self-hosted fonts for udchen.tw

Active display fonts (2026-10-20)
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
Other Chinese text falls back to Noto Sans TC.
These display faces are declared in assets/css/udc-type.css.

Reading fonts and earlier display assets
---------------------------------------
Source Sans 3 and Noto Sans TC remain active for reading.
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
