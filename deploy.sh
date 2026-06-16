#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Creating .env from defaults — set OPENROUTER_API_KEY for AI features."
  cat > .env <<'EOF'
OPENROUTER_API_KEY=
POSTGRES_PASSWORD=apidebug
FRONTEND_PORT=80
PUBLIC_URL=http://localhost
LLM_MODEL=openai/gpt-4o-mini
EMBEDDING_MODEL=openai/text-embedding-3-small
EOF
fi

echo "Building and starting production stack..."
docker compose -f docker-compose.prod.yml up --build -d

echo ""
echo "Production deploy complete."
echo "  App:  http://localhost:${FRONTEND_PORT:-80}"
echo "  API:  http://localhost:${FRONTEND_PORT:-80}/api/analytics"
echo "  Health: http://localhost:${FRONTEND_PORT:-80}/health"
