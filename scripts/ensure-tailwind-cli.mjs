import { chmodSync, existsSync, rmSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const launcher = resolve('node_modules/.bin/tailwindcss');
const cli = resolve('node_modules/@tailwindcss/cli/dist/index.mjs');

if (!existsSync(cli)) {
  throw new Error('Tailwind CLI is missing. Run pnpm install first.');
}

rmSync(launcher, { force: true });
writeFileSync(launcher, '#!/usr/bin/env node\nimport "../@tailwindcss/cli/dist/index.mjs";\n');
chmodSync(launcher, 0o755);
