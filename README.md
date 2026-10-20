# Uei-Dar Chen — Usually Depends on Context

Personal website of Uei-Dar Chen, an HCI researcher and developer studying personal agents, information management, and context-aware systems.

The site uses Hugo Blox. Most content lives in `content/`. Custom homepage and About blocks live in `layouts/partials/hbx/blocks/`; shared navigation, footer and archive templates live in `layouts/_partials/`.

The approved English/Traditional Chinese introduction, news and selected work live in `data/udc.yaml`. Homepage and About read the same introduction. Education, experience and skills come from `content/authors/admin/_index.md`; the downloadable CV is `static/uploads/uei-dar-chen-cv.pdf`.

Research lists use Hugo Blox’s Collection block; icons use its built-in icon renderer and profile data. Visual styles and preference controls live under `assets/`. Fonts are self-hosted under `static/fonts/`, with their source information and licenses included. New visitors follow their system color scheme and browser language; manual choices are remembered locally.

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
