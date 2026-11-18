# Build tools for the 2026-11 redesign

Scripts that produce the fonts, textures, plates and captures, and that run the checks. Downloads and
non-redistributable sources live outside the repo (`<dl>`, and `docs/design/v2/sources/`, which is never
committed); only outputs land in `static/` and `data/`. Python: fontTools, brotli, numpy, scipy, PIL,
pyyaml; ImageMagick 7 (`magick`) for ordered dithering. Hugo 0.170.0 (what `.github/workflows/deploy.yml` pins).

| Script | Makes or checks | Run |
|---|---|---|
| `fonts.py` | WOFF2 subsets of the six faces (static/fonts/) | `python fonts.py <repo> <dl>` |
| `noto_slices.py` | Noto Serif TC unicode-range slices for any weight | `python noto_slices.py <repo> <NotoSerifTC-VF.ttf> 900` |
| `textures.py` | Paper base layers; `sheet`: creases and worn edges; `night`: night fibre layer | `python textures.py <repo> sheet <Paper005 displacement.jpg>` |
| `halftone.py` | Plates: ryan, portrait, stadium, flag, jingu, hogwarts, thames, pages, figure404, night | `python halftone.py <repo> <plate> …` |
| `lettering.py` | 陳威達 rendered as an image (the font never ships) | `python lettering.py <repo> name <font.ttf>` |
| `flightmap.py` | About flight map: land dots + data/flight_map.json | `python flightmap.py <repo> <ne_110m_land.shp> <ne_10m_airports.shp>` |
| `paper_contrast.py` | Paper-only per-pixel contrast check, light or dark | `python paper_contrast.py <url> <outdir> [light\|dark]` |
| `shoot.mjs` | Screenshots and page measurements via headless Chrome | `node shoot.mjs jobs.json` |
| `weights.mjs` | First-view font and image bytes | `node weights.mjs <url> <width>` |
| `sharing-card.html` | Layout of the social preview card (assets/media/sharing.jpg) | serve a build, capture `.c` at 1200×630 |

Removed 2026-11-16 with the variations: check.mjs, cjk_spec.py, frames.mjs, hk_tw.py, paper_generated.py
(recoverable from commit 178802a).
