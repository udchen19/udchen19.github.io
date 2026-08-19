# U-D-C — Usually Depends on Context

Personal website of Uei-Dar Chen, an HCI researcher and developer studying personal agents, information management, and context-aware systems.

The site uses Hugo Blox. Most content lives in `content/`; the custom homepage is intentionally isolated in `layouts/partials/hbx/blocks/udc-home/`, with its styles and UI-language switcher under `assets/`.

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
