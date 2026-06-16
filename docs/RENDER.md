# Deploy on Render

Repository: [ksy2912/AI-API-DEBUGGER](https://github.com/ksy2912/AI-API-DEBUGGER)

## One-click Blueprint

1. Sign in at [dashboard.render.com](https://dashboard.render.com/)
2. Click **New +** → **Blueprint**
3. Connect your GitHub account if not already linked
4. Select repository **ksy2912/AI-API-DEBUGGER**
5. Render reads `render.yaml` and creates these resources:

| Service | Type | Purpose |
|---------|------|---------|
| `apidebug-db` | PostgreSQL | App database |
| `apidebug-redis` | Redis | Celery broker |
| `ai-api-debugger-api` | Web Service | FastAPI backend |
| `ai-api-debugger-worker` | Background Worker | Celery + beat |
| `ai-api-debugger-frontend` | Static Site | React dashboard |

6. Click **Apply** and wait for all services to deploy (~5–10 min on free tier)

## Required: OpenRouter API Key

After the first deploy:

1. Open **ai-api-debugger-api** in Render Dashboard
2. Go to **Environment**
3. Add or set `OPENROUTER_API_KEY` = your key from [openrouter.ai/keys](https://openrouter.ai/keys)
4. Copy the same key to **ai-api-debugger-worker** → Environment
5. Click **Manual Deploy** → **Deploy latest commit** on both services

## Live URLs

After deploy completes:

| Resource | URL |
|----------|-----|
| Frontend | `https://ai-api-debugger-frontend.onrender.com` |
| API | `https://ai-api-debugger-api.onrender.com` |
| Swagger docs | `https://ai-api-debugger-api.onrender.com/docs` |
| Health | `https://ai-api-debugger-api.onrender.com/health` |

## Free Tier Notes

- Services **spin down after inactivity** — first request may take 30–60 seconds
- Render Postgres **does not support pgvector** — `RAG_ENABLED=false` in `render.yaml` (LLM debug still works)
- Redis free instance has memory limits — fine for demo/monitoring workloads

## Troubleshooting

**API build fails**
- Check logs for `pip install` errors
- Ensure `PYTHON_VERSION=3.12.0` is set (already in `render.yaml`)

**Migrations fail**
- Open **apidebug-db** → **Connect** → verify `DATABASE_URL` on API service matches
- API start command runs `alembic upgrade head` automatically

**Frontend shows API errors**
- Confirm `VITE_API_URL` on frontend points to API hostname (set via `render.yaml`)
- Redeploy frontend after API is live

**CORS**
- API allows all origins (`*`) — no CORS config needed for separate frontend host

## Redeploy after code changes

Push to `main` on GitHub — Render auto-deploys if enabled (default for Blueprint services).

```bash
git add .
git commit -m "your message"
git push origin main
```
