# Uei-Dar Chen — Usually Depends on Context

Personal website of Uei-Dar Chen, an HCI researcher and developer studying personal agents, information management, and context-aware systems.

The site uses Hugo Blox. Most content lives in `content/`. Custom homepage and About blocks live in `layouts/partials/hbx/blocks/`; shared navigation, footer and archive templates live in `layouts/_partials/`.

The approved English/Traditional Chinese introduction, news and selected work live in `data/udc.yaml`. Homepage and About read the same introduction. Education, experience and skills come from `content/authors/admin/_index.md`; the downloadable CV is `static/uploads/uei-dar-chen-cv.pdf`.

Research lists use Hugo Blox’s Collection block; icons use its built-in icon renderer and profile data. Visual styles and preference controls live under `assets/`. Fonts are self-hosted under `static/fonts/`, with their source information and licenses included. New visitors follow their system color scheme and browser language; manual choices are remembered locally.

The homepage uses warm paper, orange type and rules, and green details. Fraunces and Chiron Sung HK form a shared English/Traditional Chinese type system across navigation, headings, and body text, including existing articles. The full introduction, news, selected work, and posts share an editorial margin. See `static/fonts/README.txt` for sources and licenses. Light and dark paper textures live in `static/textures/field-paper*.svg`. They combine pulp variation, grain, and fibers. Display headings use `ink-density.svg` and a luminance mask (`ink-wear.svg`) for mottled ink and small irregular gaps; body text and controls remain solid. Print, forced-colors, and increased-contrast preferences disable these effects. The small footer mascot is built from `assets/media/ryan-head.png` into a 96px WebP, displayed at 28px.

A stadium halftone sits behind the homepage’s log and footer without adding page height. Its orange 外野那群人 flag has its pole planted in the left outfield stands. A blue Sawamura Eijun manga halftone rises above right outfield, fading into the top of the stands. All three layers share photograph-relative coordinates and scale together at every viewport. Mobile reframes the entire scene, preserving their relative positions and sizes; the 500px minimum canvas keeps both accents in view down to a 320px viewport. These details are decorative and hidden from assistive technology. Sources are listed on `/design-credits/`.

## Local development

```bash
pnpm install
pnpm run dev
```

## Production build

```bash
pnpm run build
```

Articles are published in their original language. The English/Traditional Chinese switch changes interface copy only; it does not create translated copies of posts.

Pushing `main` runs `.github/workflows/deploy.yml` and deploys the generated site to GitHub Pages at `https://udchen.tw/`.
