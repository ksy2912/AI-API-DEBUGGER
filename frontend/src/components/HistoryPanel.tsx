import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  Bot,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock,
  History,
  XCircle,
} from "lucide-react";
import {
  fetchHistoryDebugSessions,
  fetchHistoryMonitors,
  fetchHistoryRuns,
} from "../api/client";
import type { DebugSession, RequestRun } from "../types/debug";
import "./HistoryPanel.css";

type HistoryTab = "runs" | "debug" | "monitors";

interface MonitorRow {
  id: string;
  name: string;
  interval_seconds: number;
  enabled: boolean;
  last_run_at: string | null;
  created_at: string;
}

const PAGE_SIZE = 15;

export default function HistoryPanel() {
  const [tab, setTab] = useState<HistoryTab>("runs");
  const [page, setPage] = useState(0);
  const [filter, setFilter] = useState<"all" | "failed" | "success">("all");
  const [runs, setRuns] = useState<RequestRun[]>([]);
  const [sessions, setSessions] = useState<DebugSession[]>([]);
  const [monitors, setMonitors] = useState<MonitorRow[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    const skip = page * PAGE_SIZE;
    try {
      if (tab === "runs") {
        const success =
          filter === "all" ? undefined : filter === "success" ? true : false;
        const data = await fetchHistoryRuns(skip, PAGE_SIZE, success);
        setRuns(data.items);
        setTotal(data.total);
      } else if (tab === "debug") {
        const data = await fetchHistoryDebugSessions(skip, PAGE_SIZE);
        setSessions(data.items);
        setTotal(data.total);
      } else {
        const data = await fetchHistoryMonitors(skip, PAGE_SIZE);
        setMonitors(data.items);
        setTotal(data.total);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load history");
    } finally {
      setLoading(false);
    }
  }, [tab, page, filter]);

  useEffect(() => {
    load();
  }, [load]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const switchTab = (next: HistoryTab) => {
    setTab(next);
    setPage(0);
  };

  return (
    <div className="history-panel">
      <header className="history-header animate-in">
        <div className="brand">
          <div className="brand-icon history-icon">
            <History size={22} />
          </div>
          <div>
            <h1>History</h1>
            <p>Paginated runs, debug sessions, and monitor schedules</p>
          </div>
        </div>
      </header>

      <div className="history-toolbar animate-in">
        <div className="history-tabs">
          <button
            className={`hist-tab ${tab === "runs" ? "active" : ""}`}
            onClick={() => switchTab("runs")}
          >
            <Activity size={15} />
            Runs
          </button>
          <button
            className={`hist-tab ${tab === "debug" ? "active" : ""}`}
            onClick={() => switchTab("debug")}
          >
            <Bot size={15} />
            Debug sessions
          </button>
          <button
            className={`hist-tab ${tab === "monitors" ? "active" : ""}`}
            onClick={() => switchTab("monitors")}
          >
            <Clock size={15} />
            Monitors
          </button>
        </div>

        {tab === "runs" && (
          <div className="filter-chips">
            {(["all", "failed", "success"] as const).map((f) => (
              <button
                key={f}
                className={`filter-chip ${filter === f ? "active" : ""}`}
                onClick={() => {
                  setFilter(f);
                  setPage(0);
                }}
              >
                {f}
              </button>
            ))}
          </div>
        )}
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="history-table-wrap animate-in" style={{ animationDelay: "60ms" }}>
        {loading ? (
          <div className="skeleton history-skeleton" />
        ) : tab === "runs" ? (
          <table className="history-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Method</th>
                <th>URL</th>
                <th>Code</th>
                <th>Latency</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {runs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="empty-cell">
                    No runs found
                  </td>
                </tr>
              ) : (
                runs.map((run) => (
                  <tr key={run.id}>
                    <td>
                      {run.success ? (
                        <CheckCircle2 size={16} className="ok-icon" />
                      ) : (
                        <XCircle size={16} className="fail-icon" />
                      )}
                    </td>
                    <td>
                      <span className={`method-badge method-${run.method.toLowerCase()}`}>
                        {run.method}
                      </span>
                    </td>
                    <td className="mono url-cell" title={run.url}>
                      {run.url}
                    </td>
                    <td>{run.status_code ?? "—"}</td>
                    <td>{run.latency_ms.toFixed(0)} ms</td>
                    <td className="muted">{new Date(run.created_at).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        ) : tab === "debug" ? (
          <table className="history-table">
            <thead>
              <tr>
                <th>Mode</th>
                <th>Summary</th>
                <th>LLM</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {sessions.length === 0 ? (
                <tr>
                  <td colSpan={4} className="empty-cell">
                    No debug sessions yet
                  </td>
                </tr>
              ) : (
                sessions.map((s) => (
                  <tr key={s.id}>
                    <td>
                      <span className={`mode-tag ${s.mode}`}>
                        {s.mode === "single" ? "Single LLM" : "Multi-agent"}
                      </span>
                    </td>
                    <td className="summary-cell">
                      {s.cause || s.root_cause || s.diagnosis || "—"}
                    </td>
                    <td>
                      <span className={`llm-badge small ${s.llm_used ? "on" : "off"}`}>
                        {s.llm_used ? "LLM" : "Heuristic"}
                      </span>
                    </td>
                    <td className="muted">{new Date(s.created_at).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        ) : (
          <table className="history-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Interval</th>
                <th>Enabled</th>
                <th>Last run</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {monitors.length === 0 ? (
                <tr>
                  <td colSpan={5} className="empty-cell">
                    No monitors configured
                  </td>
                </tr>
              ) : (
                monitors.map((m) => (
                  <tr key={m.id}>
                    <td>{m.name}</td>
                    <td>{m.interval_seconds}s</td>
                    <td>{m.enabled ? "Yes" : "No"}</td>
                    <td className="muted">
                      {m.last_run_at ? new Date(m.last_run_at).toLocaleString() : "Never"}
                    </td>
                    <td className="muted">{new Date(m.created_at).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      <footer className="history-pagination">
        <span className="page-info">
          {total} total · page {page + 1} of {totalPages}
        </span>
        <div className="page-btns">
          <button disabled={page === 0} onClick={() => setPage((p) => p - 1)}>
            <ChevronLeft size={16} />
            Prev
          </button>
          <button disabled={page + 1 >= totalPages} onClick={() => setPage((p) => p + 1)}>
            Next
            <ChevronRight size={16} />
          </button>
        </div>
      </footer>
    </div>
  );
}
