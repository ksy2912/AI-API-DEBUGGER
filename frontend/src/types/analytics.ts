export interface KpiMetrics {
  total_runs: number;
  success_count: number;
  failure_count: number;
  success_rate: number;
  failure_rate: number;
  avg_latency_ms: number;
  p95_latency_ms: number;
}

export interface TrafficBucket {
  bucket: string;
  total: number;
  success_count: number;
  failure_count: number;
}

export interface LatencyBucket {
  bucket: string;
  avg_latency_ms: number;
  p95_latency_ms: number;
}

export interface EndpointUsage {
  url: string;
  method: string;
  total: number;
  success_rate: number;
}

export interface TopFailingEndpoint {
  url: string;
  method: string;
  failure_count: number;
  last_seen: string | null;
  last_error: string | null;
}

export interface AnalyticsResponse {
  period_hours: number;
  bucket: "hour" | "day";
  kpis: KpiMetrics;
  traffic_trend: TrafficBucket[];
  latency_trend: LatencyBucket[];
  endpoint_usage: EndpointUsage[];
  top_failing: TopFailingEndpoint[];
}

export type TimeBucket = "hour" | "day";

export interface AnalyticsParams {
  hours: number;
  bucket: TimeBucket;
}
