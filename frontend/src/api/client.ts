import type { AnalyticsParams, AnalyticsResponse } from "../types/analytics";
import type { PaginatedResponse } from "../types/common";
import type {
  DebugSession,
  MultiAgentDebugResponse,
  RequestRun,
  SingleDebugResponse,
} from "../types/debug";
import type {
  GenerateTestsRequest,
  GeneratedTestCase,
  GeneratedTestResponse,
} from "../types/tests";

function resolveApiBase(): string {
  const raw = (import.meta.env.VITE_API_URL ?? "").trim();
  if (!raw) return "";
  if (raw.startsWith("http://") || raw.startsWith("https://")) {
    return raw.replace(/\/$/, "");
  }
  return `https://${raw.replace(/\/$/, "")}`;
}

const API_BASE = resolveApiBase();

async function parsePaginated<T>(res: Response): Promise<PaginatedResponse<T>> {
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return res.json();
}

export async function fetchAnalytics(params: AnalyticsParams): Promise<AnalyticsResponse> {
  const query = new URLSearchParams({
    hours: String(params.hours),
    bucket: params.bucket,
  });
  const res = await fetch(`${API_BASE}/api/analytics?${query}`);
  if (!res.ok) {
    throw new Error(`Analytics request failed (${res.status})`);
  }
  return res.json();
}

export async function fetchHealth(): Promise<{ status: string; app: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("API unreachable");
  return res.json();
}

export async function fetchFailedRuns(limit = 30): Promise<RequestRun[]> {
  const res = await fetch(`${API_BASE}/api/runs?success=false&limit=${limit}`);
  const data = await parsePaginated<RequestRun>(res);
  return data.items;
}

export async function fetchHistoryRuns(
  skip = 0,
  limit = 20,
  success?: boolean
): Promise<PaginatedResponse<RequestRun>> {
  const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
  if (success !== undefined) params.set("success", String(success));
  const res = await fetch(`${API_BASE}/api/history/runs?${params}`);
  return parsePaginated<RequestRun>(res);
}

export async function fetchHistoryDebugSessions(
  skip = 0,
  limit = 20
): Promise<PaginatedResponse<DebugSession>> {
  const res = await fetch(
    `${API_BASE}/api/history/debug-sessions?skip=${skip}&limit=${limit}`
  );
  return parsePaginated<DebugSession>(res);
}

export async function fetchHistoryMonitors(skip = 0, limit = 20) {
  const res = await fetch(`${API_BASE}/api/history/monitors?skip=${skip}&limit=${limit}`);
  if (!res.ok) throw new Error("Failed to load monitors");
  return res.json();
}

export async function debugSingle(runId: string): Promise<SingleDebugResponse> {
  const res = await fetch(`${API_BASE}/api/debug/runs/${runId}/analyze`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Debug failed (${res.status})`);
  }
  return res.json();
}

export async function debugMultiAgent(runId: string): Promise<MultiAgentDebugResponse> {
  const res = await fetch(`${API_BASE}/api/debug/runs/${runId}/multi-agent`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Multi-agent debug failed (${res.status})`);
  }
  return res.json();
}

export async function fetchDebugSessions(limit = 20): Promise<DebugSession[]> {
  const res = await fetch(`${API_BASE}/api/debug/sessions?limit=${limit}`);
  const data = await parsePaginated<DebugSession>(res);
  return data.items;
}

export async function generateTests(
  payload: GenerateTestsRequest
): Promise<GeneratedTestResponse> {
  const res = await fetch(`${API_BASE}/api/generate-tests`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ count: 5, ...payload }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Test generation failed (${res.status})`);
  }
  return res.json();
}

export async function fetchGeneratedTests(
  skip = 0,
  limit = 50
): Promise<PaginatedResponse<GeneratedTestCase>> {
  const res = await fetch(`${API_BASE}/api/generate-tests?skip=${skip}&limit=${limit}`);
  return parsePaginated<GeneratedTestCase>(res);
}

export async function triggerDemoFailure(): Promise<RequestRun> {
  const res = await fetch(`${API_BASE}/api/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      method: "GET",
      url: "https://httpbin.org/status/401",
      headers: { Accept: "application/json" },
      auth_type: "none",
    }),
  });
  const data = await res.json();
  if (!data.run_id) throw new Error("Demo request did not persist a run");
  const runRes = await fetch(`${API_BASE}/api/runs/${data.run_id}`);
  return runRes.json();
}
