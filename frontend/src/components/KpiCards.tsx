import type { CSSProperties } from "react";
import {
  Activity,
  AlertTriangle,
  Clock,
  Gauge,
  RefreshCw,
  TrendingUp,
  Zap,
} from "lucide-react";
import type { KpiMetrics } from "../types/analytics";

interface Props {
  kpis: KpiMetrics;
  loading?: boolean;
}

const cards = [
  {
    key: "total",
    label: "Total Runs",
    icon: Activity,
    color: "var(--chart-1)",
    getValue: (k: KpiMetrics) => k.total_runs.toLocaleString(),
    sub: "requests executed",
  },
  {
    key: "success",
    label: "Success Rate",
    icon: TrendingUp,
    color: "var(--success)",
    getValue: (k: KpiMetrics) => `${k.success_rate}%`,
    sub: (k: KpiMetrics) => `${k.success_count} passed`,
  },
  {
    key: "failure",
    label: "Failure Rate",
    icon: AlertTriangle,
    color: "var(--danger)",
    getValue: (k: KpiMetrics) => `${k.failure_rate}%`,
    sub: (k: KpiMetrics) => `${k.failure_count} failed`,
  },
  {
    key: "avg",
    label: "Avg Latency",
    icon: Clock,
    color: "var(--warning)",
    getValue: (k: KpiMetrics) => `${k.avg_latency_ms} ms`,
    sub: "mean response time",
  },
  {
    key: "p95",
    label: "P95 Latency",
    icon: Gauge,
    color: "var(--chart-3)",
    getValue: (k: KpiMetrics) => `${k.p95_latency_ms} ms`,
    sub: "95th percentile",
  },
] as const;

export default function KpiCards({ kpis, loading }: Props) {
  return (
    <div className="kpi-grid">
      {cards.map((card, i) => {
        const Icon = card.icon;
        const sub = typeof card.sub === "function" ? card.sub(kpis) : card.sub;
        return (
          <div
            key={card.key}
            className={`kpi-card animate-in ${loading ? "loading" : ""}`}
            style={{ animationDelay: `${i * 60}ms`, "--accent-color": card.color } as CSSProperties}
          >
            {loading ? (
              <div className="skeleton kpi-skeleton" />
            ) : (
              <>
                <div className="kpi-header">
                  <span className="kpi-icon" style={{ background: `${card.color}22`, color: card.color }}>
                    <Icon size={18} />
                  </span>
                  <span className="kpi-label">{card.label}</span>
                </div>
                <div className="kpi-value">{card.getValue(kpis)}</div>
                <div className="kpi-sub">{sub}</div>
              </>
            )}
          </div>
        );
      })}
    </div>
  );
}

export function LiveIndicator({ active }: { active: boolean }) {
  return (
    <span className={`live-dot ${active ? "on" : ""}`}>
      <Zap size={12} />
      {active ? "Live" : "Paused"}
    </span>
  );
}
