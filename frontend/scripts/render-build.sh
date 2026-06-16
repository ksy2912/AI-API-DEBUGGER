#!/usr/bin/env bash
set -euo pipefail

if [[ -n "${VITE_API_URL:-}" && ! "$VITE_API_URL" =~ ^https?:// ]]; then
  export VITE_API_URL="https://${VITE_API_URL}"
fi

npm install
npm run build
