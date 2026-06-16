# Five Hardest Problems Solved

## 1. LangGraph Node Name vs State Key Collision

**Problem:** The multi-agent debugger defined a graph node named `root_cause` while the shared state object also had a `root_cause` field. LangGraph treated the node name as conflicting with state, causing runtime errors.

**Solution:** Renamed the node to `root_cause_analyst` while keeping the state key `root_cause`. This is a subtle LangGraph convention — node IDs must not collide with state channel names.

---

## 2. Celery Worker Migration Race

**Problem:** Running `alembic upgrade head` in both the API container and the Celery worker caused concurrent migration attempts on startup, occasionally crashing the worker.

**Solution:** Migrations run only in the `api` service command. Worker and beat start Celery directly after DB is healthy.

---

## 3. SQLAlchemy Enum Value Mismatch

**Problem:** PostgreSQL enums store lowercase values (`none`, `bearer`) but SQLAlchemy was emitting uppercase names (`NONE`, `BEARER`), causing insert failures.

**Solution:** Added `values_callable=lambda e: [v.value for v in e]` on all `Enum` columns so the ORM sends Python enum values, not member names.

---

## 4. RAG with pgvector in Docker

**Problem:** Standard `postgres:16-alpine` does not include the `vector` extension. Embedding storage and cosine-distance queries require pgvector.

**Solution:**
- Switched DB image to `pgvector/pgvector:pg16`
- Alembic migration `004` runs `CREATE EXTENSION IF NOT EXISTS vector`
- `log_embeddings` table uses `Vector(1536)` with cosine distance ordering
- Graceful fallback: if RAG/embeddings fail, debug still works without retrieved context

**Note:** Existing volumes created with plain Postgres may need `docker compose down -v` once when switching images.

---

## 5. Dev vs Production Frontend API Routing

**Problem:** Vite dev server uses a proxy (`/api` → backend), but a production static build needs either a baked-in API URL or a reverse proxy.

**Solution:**
- **Dev:** `VITE_API_URL=http://localhost:8010` + Vite proxy for hot reload
- **Prod:** `VITE_API_URL=""` (relative URLs) + nginx proxies `/api/` and `/health` to the internal API service

This avoids CORS issues and keeps one Docker network for all services.

---

## Honorable Mentions

| Issue | Fix |
|-------|-----|
| DNS / bad URLs in executor | Friendly error messages + URL validation |
| AI Debugger tab not visible | Prominent nav + hash routing (`#debug`) |
| OpenRouter vs OpenAI | Single `llm.py` client with configurable `base_url` |
| Heuristic fallback | All AI features work without API key for demos |
