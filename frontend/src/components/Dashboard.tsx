import { useCallback, useEffect, useState } from "react";
import { BarChart3, Bot, RefreshCw } from "lucide-react";
import { fetchAnalytics, fetchHealth } from "../api/client";
import type { AnalyticsParams, AnalyticsResponse, TimeBucket } from "../types/analytics";
import KpiCards, { LiveIndicator } from "./KpiCards";
import { EndpointChart, LatencyChart, TrafficChart } from "./Charts";
import TopFailingTable from "./TopFailingTable";
import "./Dashboard.css";

const PERIODS = [
  { label: "1h", hours: 1, bucket: "hour" as TimeBucket },
  { label: "24h", hours: 24, bucket: "hour" as TimeBucket },
  { label: "7d", hours: 168, bucket: "day" as TimeBucket },
  { label: "30d", hours: 720, bucket: "day" as TimeBucket },
];

const REFRESH_INTERVAL_MS = 30_000;

export default function Dashboard({ onOpenDebugger }: { onOpenDebugger?: () => void }) {
  const [params, setParams] = useState<AnalyticsParams>({ hours: 24, bucket: "hour" });
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [apiOnline, setApiOnline] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const load = useCallback(async (showSpinner = false) => {
    if (showSpinner) setLoading(true);
    setError(null);
    try {
      await fetchHealth();
      setApiOnline(true);
      const result = await fetchAnalytics(params);
      setData(result);
      setLastUpdated(new Date());
    } catch (e) {
      setApiOnline(false);
      setError(e instanceof Error ? e.message : "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    load(true);
  }, [load]);

  useEffect(() => {
    if (!autoRefresh) return;
    const id = setInterval(() => load(false), REFRESH_INTERVAL_MS);
    return () => clearInterval(id);
  }, [autoRefresh, load]);

  const endpointChartData =
    data?.endpoint_usage.map((e) => ({
      name: e.url.replace(/^https?:\/\/[^/]+/, "") || "/",
      total: e.total,
      success_rate: e.success_rate,
      method: e.method,
    })) ?? [];

  return (
    <div className="dashboard">
      <header className="dash-header animate-in">
        <div className="brand">
          <div className="brand-icon">
            <BarChart3 size={22} />
          </div>
          <div>
            <h1>API Analytics</h1>
            <p>Real-time performance & reliability dashboard</p>
          </div>
        </div>
        <div className="header-actions">
          <LiveIndicator active={autoRefresh && apiOnline} />
          <button type="button" className="btn-debugger-link" onClick={onOpenDebugger}>
            <Bot size={16} />
            AI Debugger
          </button>
          <label className="toggle">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>
          <button className="btn-icon" onClick={() => load(true)} title="Refresh now" disabled={loading}>
            <RefreshCw size={18} className={loading ? "spin" : ""} />
          </button>
        </div>
      </header>

      <div className="toolbar animate-in" style={{ animationDelay: "80ms" }}>
        <div className="period-pills">
          {PERIODS.map((p) => (
            <button
              key={p.label}
              className={`pill ${params.hours === p.hours ? "active" : ""}`}
              onClick={() => setParams({ hours: p.hours, bucket: p.bucket })}
            >
              {p.label}
            </button>
          ))}
        </div>
        {lastUpdated && (
          <span className="last-updated">
            Updated {lastUpdated.toLocaleTimeString()}
          </span>
        )}
      </div>

      {error && (
        <div className="error-banner animate-in">
          <strong>Connection issue</strong> — {error}. Is the API running on port 8010?
        </div>
      )}

      <KpiCards kpis={data?.kpis ?? emptyKpis} loading={loading && !data} />

      <div className="charts-grid">
        <section className="chart-card animate-in" style={{ animationDelay: "120ms" }}>
          <h2>Traffic volume</h2>
          <p className="chart-desc">Success vs failed requests over time</p>
          {loading && !data ? <div className="skeleton chart-skeleton" /> : <TrafficChart data={data?.traffic_trend ?? []} />}
        </section>

        <section className="chart-card animate-in" style={{ animationDelay: "160ms" }}>
          <h2>Latency trends</h2>
          <p className="chart-desc">Average and P95 response time (ms)</p>
          {loading && !data ? <div className="skeleton chart-skeleton" /> : <LatencyChart data={data?.latency_trend ?? []} />}
        </section>

        <section className="chart-card wide animate-in" style={{ animationDelay: "200ms" }}>
          <h2>Endpoint usage</h2>
          <p className="chart-desc">Most called APIs in selected period</p>
          {loading && !data ? (
            <div className="skeleton chart-skeleton tall" />
          ) : (
            <EndpointChart data={endpointChartData} />
          )}
        </section>

        <section className="chart-card wide animate-in" style={{ animationDelay: "240ms" }}>
          <h2>Top failing APIs</h2>
          <p className="chart-desc">Click a row to expand the last error message</p>
          {loading && !data ? (
            <div className="skeleton chart-skeleton tall" />
          ) : (
            <TopFailingTable data={data?.top_failing ?? []} />
          )}
        </section>
      </div>

      <footer className="dash-footer">
        <button type="button" className="footer-debug-btn" onClick={onOpenDebugger}>
          🤖 Open AI Debugger
        </button>
        <span>·</span>
        <a href="http://localhost:8010/docs" target="_blank" rel="noreferrer">
          API Docs
        </a>
        <span>·</span>
        <span className="mono">GET /api/analytics</span>
      </footer>
    </div>
  );
}

const emptyKpis = {
  total_runs: 0,
  success_count: 0,
  failure_count: 0,
  success_rate: 0,
  failure_rate: 0,
  avg_latency_ms: 0,
  p95_latency_ms: 0,
};
