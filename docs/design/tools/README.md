# Build tools for the 2026-11 redesign (branch only)

Scripts that produced the fonts, textures and screenshots. Downloads go to a scratch
folder outside the repo (`<dl>` below); only their outputs land in `static/`.

| Script | Makes | Run |
|---|---|---|
| `fonts.py` | Glyph-coverage table `data/specimen_glyphs.json` + WOFF2 subsets in `static/fonts/` | `python fonts.py <repo> <dl>` (fontTools, brotli) |
| `cjk_spec.py` | Specimen-only 繁體中文 subsets (Noto Serif TC, Iansui) | `python cjk_spec.py <repo> <dl>` |
| `hk_tw.py` | Which characters in the posts differ between Noto Serif TC (Taiwan) and Chiron Sung HK (Hong Kong) | `python hk_tw.py <repo> <noto-400.ttf>` |
| `textures.py` | Paper, show-through, press and wear textures | `python textures.py <repo> <Paper002_Color.jpg> <Newsreader.ttf> <MetropolitanLine.ttf>` |
| `paper_generated.py` | Procedural paper for the specimen comparison | `python paper_generated.py <repo>` |
| `halftone.py` | Stadium, flag and Ryan plates (day and night) | `python halftone.py <repo>` |
| `noto_slices.py` | Noto Serif TC static 400/700 unicode-range slices | `python noto_slices.py <repo> <NotoSerifTC.ttf>` |
| `frames.mjs` | Entrance test: frames, skip, exit, second visit | `node frames.mjs <url> <out> frames|skip|exit|second` |
| `weights.mjs` / `check.mjs` | First-view font weight; 320px overflow and field lettering | `node weights.mjs <url> <width>` |
| `shoot.mjs` | Full-page screenshots via headless Chrome (no packages) | `node shoot.mjs jobs.json` |

Local server: Hugo 0.165 (what CI pins). Homebrew Hugo 0.168 rejects the Hugo Blox module's
`includeFiles` key, so `HUGO=/path/to/hugo-0.165 scripts/variations.sh`.
