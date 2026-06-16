# AI API Debugger

Developer platform for API testing, scheduled monitoring, AI debugging, RAG-augmented root-cause analysis, test generation, and SQL-backed analytics.

## Features (Days 16–30)

| Day | Feature |
|-----|---------|
| 16–20 | Collections, HTTP executor, run history, environments, Celery monitoring |
| 21–23 | SQL analytics (P95, success %) + Recharts dashboard |
| 24 | Single-LLM failure analysis |
| 25 | LangGraph multi-agent debugger |
| 26 | pgvector RAG — similar incident retrieval |
| 27 | LLM test case generator |
| 28 | Paginated history API + History UI |
| 29 | Production Docker (nginx + one-command deploy) |
| 30 | Architecture docs + demo walkthrough |

## Quick Start (Development)

```bash
# 1. Set your OpenRouter key in .env (project root)
# OPENROUTER_API_KEY=sk-or-v1-...

docker compose up --build
```

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:5173 |
| API docs | http://localhost:8010/docs |
| Analytics API | http://localhost:8010/api/analytics |

### UI Tabs

| Tab | URL |
|-----|-----|
| Analytics | http://localhost:5173 |
| AI Debugger | http://localhost:5173/#debug |
| Test Generator | http://localhost:5173/#tests |
| History | http://localhost:5173/#history |

## Production Deploy

```powershell
.\deploy.ps1
```

```bash
chmod +x deploy.sh && ./deploy.sh
```

Opens at http://localhost (port configurable via `FRONTEND_PORT` in `.env`).

## Environment

Create `.env` in the project root:

```env
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-4o-mini
LLM_ENABLED=true
EMBEDDING_MODEL=openai/text-embedding-3-small
RAG_ENABLED=true
RAG_TOP_K=5
```

Without `OPENROUTER_API_KEY`, AI features use **heuristic fallback** (still functional for demos).

Get a key at https://openrouter.ai/keys

## API Highlights

| Endpoint | Description |
|----------|-------------|
| `POST /api/execute` | Execute HTTP request, persist run |
| `GET /api/analytics` | Dashboard metrics |
| `POST /api/debug/analyze` | Single-LLM debug (with RAG context) |
| `POST /api/debug/multi-agent` | LangGraph pipeline |
| `POST /api/generate-tests` | Generate API test cases |
| `GET /api/history/runs` | Paginated run history |
| `GET /api/history/debug-sessions` | Paginated debug sessions |

Full API: http://localhost:8010/docs

## Stack

- **Backend:** Python, FastAPI, SQLAlchemy, Alembic, httpx, Celery, LangGraph
- **Database:** PostgreSQL 16 + pgvector
- **Cache/Queue:** Redis
- **AI:** OpenRouter (chat + embeddings)
- **Frontend:** React, Vite, Recharts, Lucide icons

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — system diagram and data flow
- [Demo walkthrough](docs/DEMO.md) — step-by-step guide
- [Hardest problems](docs/HARDEST_PROBLEMS.md) — technical challenges solved

## Deploy on Render

Repository: [github.com/ksy2912/AI-API-DEBUGGER](https://github.com/ksy2912/AI-API-DEBUGGER)

1. Push this repo to GitHub (see below).
2. Go to [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**.
3. Connect the `ksy2912/AI-API-DEBUGGER` repo — Render reads `render.yaml` automatically.
4. After deploy starts, open the **ai-api-debugger-api** service → **Environment** → set `OPENROUTER_API_KEY` (required for LLM features).
5. Redeploy if needed. Live URLs:
   - **Frontend:** `https://ai-api-debugger-frontend.onrender.com`
   - **API:** `https://ai-api-debugger-api.onrender.com`
   - **API docs:** `https://ai-api-debugger-api.onrender.com/docs`

`render.yaml` provisions: PostgreSQL, Redis, API web service, Celery worker (+ beat), and static frontend.

> **Note:** Render free Postgres does not include pgvector — `RAG_ENABLED` defaults to `false` on Render. Use Docker locally for full RAG.

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: AI API Debugger (Days 16-30)"
git branch -M main
git remote add origin https://github.com/ksy2912/AI-API-DEBUGGER.git
git push -u origin main
```

## pgvector Note

The database image is `pgvector/pgvector:pg16`. If upgrading from an older plain-Postgres volume:

```bash
docker compose down -v   # removes data — backup first if needed
docker compose up --build
```

## Project Structure

```
backend/app/
  routers/     # FastAPI routes
  services/    # executor, analytics, llm, rag, multi-agent debug
  models/      # SQLAlchemy models
  alembic/     # migrations (001–004)

frontend/src/
  components/  # Dashboard, DebugPanel, TestsPanel, HistoryPanel
  api/         # fetch client
```
