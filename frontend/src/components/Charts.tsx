import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TrafficBucket } from "../types/analytics";

function formatBucket(value: string) {
  const d = new Date(value);
  return d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit" });
}

function shortUrl(url: string) {
  try {
    const u = new URL(url);
    return u.pathname.length > 30 ? u.pathname.slice(0, 30) + "…" : u.pathname || u.host;
  } catch {
    return url.slice(0, 32);
  }
}

export function TrafficChart({ data }: { data: TrafficBucket[] }) {
  if (!data.length) {
    return <EmptyChart message="No traffic data in this period" />;
  }

  const chartData = data.map((d) => ({
    ...d,
    label: formatBucket(d.bucket),
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="successGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#22c55e" stopOpacity={0.4} />
            <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="failGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ef4444" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
        <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} tickLine={false} axisLine={false} allowDecimals={false} />
        <Tooltip
          contentStyle={{
            background: "#161d2e",
            border: "1px solid rgba(148,163,184,0.15)",
            borderRadius: 10,
            color: "#f1f5f9",
          }}
        />
        <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
        <Area
          type="monotone"
          dataKey="success_count"
          name="Success"
          stroke="#22c55e"
          fill="url(#successGrad)"
          strokeWidth={2}
          stackId="1"
        />
        <Area
          type="monotone"
          dataKey="failure_count"
          name="Failed"
          stroke="#ef4444"
          fill="url(#failGrad)"
          strokeWidth={2}
          stackId="1"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function LatencyChart({
  data,
}: {
  data: { bucket: string; avg_latency_ms: number; p95_latency_ms: number }[];
}) {
  if (!data.length) {
    return <EmptyChart message="No latency data in this period" />;
  }

  const chartData = data.map((d) => ({
    ...d,
    label: formatBucket(d.bucket),
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="avgGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#818cf8" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#818cf8" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
        <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          unit=" ms"
        />
        <Tooltip
          contentStyle={{
            background: "#161d2e",
            border: "1px solid rgba(148,163,184,0.15)",
            borderRadius: 10,
            color: "#f1f5f9",
          }}
          formatter={(v: number) => [`${v} ms`, ""]}
        />
        <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
        <Area
          type="monotone"
          dataKey="avg_latency_ms"
          name="Avg"
          stroke="#818cf8"
          fill="url(#avgGrad)"
          strokeWidth={2}
        />
        <Area
          type="monotone"
          dataKey="p95_latency_ms"
          name="P95"
          stroke="#f472b6"
          fill="none"
          strokeWidth={2}
          strokeDasharray="6 4"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function EndpointChart({
  data,
}: {
  data: { name: string; total: number; success_rate: number; method: string }[];
}) {
  if (!data.length) {
    return <EmptyChart message="No endpoint usage yet" />;
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(200, data.length * 44)}>
      <BarChart layout="vertical" data={data} margin={{ top: 4, right: 24, left: 8, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" horizontal={false} />
        <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis
          type="category"
          dataKey="name"
          width={140}
          tick={{ fill: "#94a3b8", fontSize: 10 }}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip
          contentStyle={{
            background: "#161d2e",
            border: "1px solid rgba(148,163,184,0.15)",
            borderRadius: 10,
            color: "#f1f5f9",
          }}
          formatter={(v: number, _n, item) => [
            `${v} calls · ${item.payload.success_rate}% success`,
            item.payload.method,
          ]}
        />
        <Bar dataKey="total" name="Calls" fill="#6366f1" radius={[0, 6, 6, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export { shortUrl };

function EmptyChart({ message }: { message: string }) {
  return (
    <div className="chart-empty">
      <p>{message}</p>
      <span>Execute some API requests to populate analytics</span>
    </div>
  );
}
