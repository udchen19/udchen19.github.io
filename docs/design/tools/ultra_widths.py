"""Ultra's real letter widths, for sizing page titles (Astra review, rounds 3 and 4).

python ultra_widths.py <repo>

Reads the Ultra subset the site serves (static/fonts/udc-ultra.woff2) and writes data/ultra_widths.json:
  adv   each character's advance width, in em
  kern  each kerning pair's adjustment, in em (the font's legacy 'kern' table; it has no GPOS)
  max   the widest advance, used for a character the subset lacks
layouts/_partials/udc/single.html adds these up for the longest unbreakable piece of a title, so the
title shrinks on narrow screens only as much as that piece needs. Re-run after re-subsetting Ultra.
"""
import sys, json, pathlib
from fontTools.ttLib import TTFont

repo = pathlib.Path(sys.argv[1])
font = TTFont(repo / "static/fonts/udc-ultra.woff2")
upem = font["head"].unitsPerEm
cmap = font.getBestCmap()
hmtx = font["hmtx"]
glyph_char = {}
for code, glyph in cmap.items():
    glyph_char.setdefault(glyph, chr(code))
adv = {chr(code): round(hmtx[glyph][0] / upem, 4) for code, glyph in cmap.items()}
kern = {}
if "kern" in font:
    for table in font["kern"].kernTables:
        for (left, right), value in getattr(table, "kernTable", {}).items():
            if left in glyph_char and right in glyph_char and value:
                kern[glyph_char[left] + glyph_char[right]] = round(value / upem, 4)
out = {"adv": adv, "kern": kern, "max": max(adv.values())}
(repo / "data/ultra_widths.json").write_text(json.dumps(out, ensure_ascii=False, sort_keys=True))
print(f"{len(adv)} characters, {len(kern)} kerning pairs, widest {out['max']} em")
