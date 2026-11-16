#!/usr/bin/env bash
# Serve the three redesign variations side by side (branch only; see plan 6.2).
#   A http://localhost:1313   B http://localhost:1314   C http://localhost:1315
# Use the Hugo version CI pins (0.165): HUGO=/path/to/hugo-0.165 scripts/variations.sh
cd "$(dirname "$0")/.." || exit 1
node scripts/ensure-tailwind-cli.mjs || exit 1
trap 'kill 0' EXIT
# Each server renders to its own folder; sharing public/ makes them overwrite each other.
OUT="${TMPDIR:-/tmp}/udc-variations"
"${HUGO:-hugo}" server -D -e va -d "$OUT/va" -p 1313 --bind 127.0.0.1 --disableFastRender &
"${HUGO:-hugo}" server -D -e vb -d "$OUT/vb" -p 1314 --bind 127.0.0.1 --disableFastRender &
"${HUGO:-hugo}" server -D -e vc -d "$OUT/vc" -p 1315 --bind 127.0.0.1 --disableFastRender &
wait
