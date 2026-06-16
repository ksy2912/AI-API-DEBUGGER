# Demo Walkthrough

End-to-end demo of the AI API Debugger in ~5 minutes.

## Prerequisites

```bash
docker compose up --build
```

Set `OPENROUTER_API_KEY` in `.env` for full LLM + RAG features.

| URL | Purpose |
|-----|---------|
| http://localhost:5173 | Dashboard UI |
| http://localhost:8010/docs | Swagger API |

---

## 1. Analytics Dashboard

1. Open http://localhost:5173 (Analytics tab).
2. KPI cards show success rate, P95 latency, total runs.
3. Charts display latency and error trends over time.

If empty, proceed to step 2 to generate data.

---

## 2. Create a Failed Run

**Option A — UI:** AI Debugger tab → **Generate demo failure**

**Option B — API:**

```bash
curl -X POST http://localhost:8010/api/execute \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","url":"https://httpbin.org/status/401","auth_type":"none"}'
```

Refresh Analytics — you should see the failed run reflected.

---

## 3. AI Debugger (Single + Multi-Agent)

1. Go to **AI Debugger** tab (or http://localhost:5173/#debug).
2. Select the failed 401 run from the sidebar.
3. **Single LLM:** click *Analyze failure* → cause + fix.
4. **Multi-Agent:** switch mode → *Run Diagnoser → Validator* → full pipeline trace + optimized request.

RAG: after a few debug sessions, similar past failures are retrieved automatically from pgvector.

---

## 4. Test Generator

1. Open **Tests** tab (http://localhost:5173/#tests).
2. Click a quick demo chip (e.g. *Auth endpoint*).
3. Click **Generate test cases**.
4. Review positive, negative, auth, and edge-case tests.

---

## 5. History

1. Open **History** tab (http://localhost:5173/#history).
2. Browse **Runs** with all/failed/success filters.
3. Switch to **Debug sessions** and **Monitors** tabs.
4. Use pagination controls at the bottom.

---

## 6. Production Deploy

```powershell
.\deploy.ps1
```

Or on Linux/macOS:

```bash
chmod +x deploy.sh && ./deploy.sh
```

Open http://localhost — nginx serves the built SPA and proxies `/api` to the backend.

---

## API Quick Reference

```bash
# Analytics
curl http://localhost:8010/api/analytics?hours=24&bucket=hour

# Debug a run (replace RUN_ID)
curl -X POST http://localhost:8010/api/debug/runs/RUN_ID/multi-agent

# Generate tests
curl -X POST http://localhost:8010/api/generate-tests \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","url":"https://httpbin.org/bearer","spec":"Auth endpoint","count":5}'

# Paginated history
curl "http://localhost:8010/api/history/runs?skip=0&limit=10&success=false"
```
