import { useCallback, useEffect, useState } from "react";
import {
  Bot,
  Brain,
  CheckCircle2,
  ChevronRight,
  FlaskConical,
  Loader2,
  Sparkles,
  XCircle,
  Zap,
} from "lucide-react";
import {
  debugMultiAgent,
  debugSingle,
  fetchDebugSessions,
  fetchFailedRuns,
  triggerDemoFailure,
} from "../api/client";
import type {
  DebugSession,
  MultiAgentDebugResponse,
  RequestRun,
  SingleDebugResponse,
} from "../types/debug";
import "./DebugPanel.css";

type DebugMode = "single" | "multi";

export default function DebugPanel() {
  const [runs, setRuns] = useState<RequestRun[]>([]);
  const [sessions, setSessions] = useState<DebugSession[]>([]);
  const [selectedRun, setSelectedRun] = useState<RequestRun | null>(null);
  const [mode, setMode] = useState<DebugMode>("multi");
  const [loading, setLoading] = useState(false);
  const [loadingRuns, setLoadingRuns] = useState(true);
  const [singleResult, setSingleResult] = useState<SingleDebugResponse | null>(null);
  const [multiResult, setMultiResult] = useState<MultiAgentDebugResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadRuns = useCallback(async () => {
    setLoadingRuns(true);
    try {
      const [failed, history] = await Promise.all([
        fetchFailedRuns(),
        fetchDebugSessions(),
      ]);
      setRuns(failed);
      setSessions(history);
      setSelectedRun((prev) => prev ?? failed[0] ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load runs");
    } finally {
      setLoadingRuns(false);
    }
  }, []);

  useEffect(() => {
    loadRuns();
  }, [loadRuns]);

  const runDebug = async () => {
    if (!selectedRun) return;
    setLoading(true);
    setError(null);
    setSingleResult(null);
    setMultiResult(null);
    try {
      if (mode === "single") {
        const result = await debugSingle(selectedRun.id);
        setSingleResult(result);
      } else {
        const result = await debugMultiAgent(selectedRun.id);
        setMultiResult(result);
      }
      await loadRuns();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Debug failed");
    } finally {
      setLoading(false);
    }
  };

  const createDemoFailure = async () => {
    setLoading(true);
    setError(null);
    try {
      const run = await triggerDemoFailure();
      setRuns((prev) => [run, ...prev]);
      setSelectedRun(run);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Demo failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="debug-panel">
      <header className="debug-header animate-in">
        <div className="brand">
          <div className="brand-icon debug-icon">
            <Bot size={22} />
          </div>
          <div>
            <h1>AI Debugger</h1>
            <p>Diagnose failures · root cause · validated fixes</p>
          </div>
        </div>
        <button className="btn-demo" onClick={createDemoFailure} disabled={loading}>
          <FlaskConical size={16} />
          Generate demo failure
        </button>
      </header>

      <div className="debug-layout">
        <aside className="runs-sidebar animate-in">
          <h3>Failed runs</h3>
          {loadingRuns ? (
            <div className="skeleton run-skeleton" />
          ) : runs.length === 0 ? (
            <div className="runs-empty">
              <XCircle size={28} />
              <p>No failed runs yet</p>
              <button className="btn-demo small" onClick={createDemoFailure}>
                Create demo 401 failure
              </button>
            </div>
          ) : (
            <ul className="runs-list">
              {runs.map((run) => (
                <li
                  key={run.id}
                  className={`run-item ${selectedRun?.id === run.id ? "active" : ""}`}
                  onClick={() => {
                    setSelectedRun(run);
                    setSingleResult(null);
                    setMultiResult(null);
                  }}
                >
                  <span className={`method-badge method-${run.method.toLowerCase()}`}>
                    {run.method}
                  </span>
                  <span className="run-url mono" title={run.url}>
                    {run.url.replace(/^https?:\/\/[^/]+/, "")}
                  </span>
                  <span className="run-status fail">{run.status_code ?? "ERR"}</span>
                </li>
              ))}
            </ul>
          )}

          {sessions.length > 0 && (
            <>
              <h3 className="history-title">Recent debug sessions</h3>
              <ul className="sessions-mini">
                {sessions.slice(0, 5).map((s) => (
                  <li key={s.id}>
                    <span className={`mode-tag ${s.mode}`}>{s.mode === "single" ? "LLM" : "Pipeline"}</span>
                    <span className="muted">{new Date(s.created_at).toLocaleTimeString()}</span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </aside>

        <main className="debug-main animate-in" style={{ animationDelay: "80ms" }}>
          {selectedRun ? (
            <>
              <div className="selected-run-card">
                <div className="run-meta">
                  <span className={`method-badge method-${selectedRun.method.toLowerCase()}`}>
                    {selectedRun.method}
                  </span>
                  <code className="mono">{selectedRun.url}</code>
                </div>
                <div className="run-stats">
                  <span className={selectedRun.success ? "ok" : "fail"}>
                    {selectedRun.success ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
                    {selectedRun.status_code ?? "Error"}
                  </span>
                  <span>{selectedRun.latency_ms} ms</span>
                  {selectedRun.error && (
                    <span className="err-preview mono">{selectedRun.error.slice(0, 60)}…</span>
                  )}
                </div>
              </div>

              <div className="mode-toggle">
                <button
                  className={`mode-btn ${mode === "single" ? "active" : ""}`}
                  onClick={() => setMode("single")}
                >
                  <Sparkles size={16} />
                  Day 24 — Single LLM
                </button>
                <button
                  className={`mode-btn ${mode === "multi" ? "active" : ""}`}
                  onClick={() => setMode("multi")}
                >
                  <Brain size={16} />
                  Day 25 — Multi-Agent Pipeline
                </button>
              </div>

              <button className="btn-debug" onClick={runDebug} disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 size={18} className="spin" />
                    {mode === "multi" ? "Running pipeline…" : "Analyzing…"}
                  </>
                ) : (
                  <>
                    <Zap size={18} />
                    {mode === "multi" ? "Run Diagnoser → Validator" : "Analyze failure"}
                  </>
                )}
              </button>

              {error && <div className="error-banner">{error}</div>}

              {singleResult && (
                <div className="result-card single-result">
                  <div className="result-header">
                    <h3>Single-LLM analysis</h3>
                    <span className={`llm-badge ${singleResult.llm_used ? "on" : "off"}`}>
                      {singleResult.llm_used ? "OpenRouter LLM" : "Heuristic mode"}
                    </span>
                  </div>
                  <div className="result-block cause">
                    <label>Likely cause</label>
                    <p>{singleResult.result.cause}</p>
                  </div>
                  <div className="result-block fix">
                    <label>Recommended fix</label>
                    <p>{singleResult.result.fix}</p>
                  </div>
                  <span className="confidence">Confidence: {singleResult.result.confidence}</span>
                </div>
              )}

              {multiResult && (
                <div className="result-card multi-result">
                  <div className="result-header">
                    <h3>Multi-agent pipeline</h3>
                    <span className={`llm-badge ${multiResult.llm_used ? "on" : "off"}`}>
                      {multiResult.llm_used ? "OpenRouter LLM" : "Heuristic mode"}
                    </span>
                    <span className={`validation ${multiResult.result.validation_passed ? "pass" : "warn"}`}>
                      {multiResult.result.validation_passed ? "Validated" : "Needs review"}
                    </span>
                  </div>

                  <div className="pipeline-trace">
                    {multiResult.result.agent_trace.map((step, i) => (
                      <div key={i} className="trace-step">
                        <div className="trace-agent">
                          <ChevronRight size={14} />
                          {step.agent}
                        </div>
                        <p>{step.output}</p>
                      </div>
                    ))}
                  </div>

                  <div className="result-grid">
                    <div className="result-block">
                      <label>Root cause</label>
                      <p>{multiResult.result.root_cause}</p>
                    </div>
                    <div className="result-block fix">
                      <label>Validated fix</label>
                      <p>{multiResult.result.validated_fix}</p>
                    </div>
                  </div>

                  <div className="optimized-request">
                    <label>Optimized request</label>
                    <pre className="mono">
                      {JSON.stringify(multiResult.result.optimized_request, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="debug-empty">
              <Bot size={48} strokeWidth={1.2} />
              <h2>Select a failed run</h2>
              <p>Or generate a demo 401 failure to test the AI debugger</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
