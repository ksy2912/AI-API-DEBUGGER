import { useCallback, useEffect, useState } from "react";
import { FlaskConical, Loader2, Sparkles, TestTube2 } from "lucide-react";
import { fetchGeneratedTests, generateTests } from "../api/client";
import type { GeneratedTestCase } from "../types/tests";
import "./TestsPanel.css";

const DEMO_SPECS = [
  {
    label: "REST CRUD",
    spec: "POST /api/users — create user with email and name",
    method: "POST",
    url: "https://httpbin.org/post",
    body: '{"email":"test@example.com","name":"Test User"}',
  },
  {
    label: "Auth endpoint",
    spec: "GET /api/profile — requires Bearer token",
    method: "GET",
    url: "https://httpbin.org/bearer",
  },
  {
    label: "Payment API",
    spec: "POST /api/payments — charge card with amount and currency",
    method: "POST",
    url: "https://httpbin.org/post",
    body: '{"amount":100,"currency":"USD","card":"4242"}',
  },
];

export default function TestsPanel() {
  const [method, setMethod] = useState("GET");
  const [url, setUrl] = useState("https://httpbin.org/status/200");
  const [spec, setSpec] = useState("");
  const [body, setBody] = useState("");
  const [count, setCount] = useState(5);
  const [tests, setTests] = useState<GeneratedTestCase[]>([]);
  const [llmUsed, setLlmUsed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadHistory = useCallback(async () => {
    setLoadingHistory(true);
    try {
      const data = await fetchGeneratedTests(0, 30);
      setTests(data.items);
    } catch {
      /* empty history is fine */
    } finally {
      setLoadingHistory(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const runGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await generateTests({
        spec: spec || `${method} ${url}`,
        method,
        url,
        body: body || null,
        headers: body ? { "Content-Type": "application/json" } : {},
        count,
      });
      setTests(result.tests);
      setLlmUsed(result.llm_used);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Generation failed");
    } finally {
      setLoading(false);
    }
  };

  const applyDemo = (demo: (typeof DEMO_SPECS)[0]) => {
    setSpec(demo.spec);
    setMethod(demo.method);
    setUrl(demo.url);
    setBody(demo.body ?? "");
  };

  return (
    <div className="tests-panel">
      <header className="tests-header animate-in">
        <div className="brand">
          <div className="brand-icon tests-icon">
            <TestTube2 size={22} />
          </div>
          <div>
            <h1>Test Generator</h1>
            <p>LLM-powered edge cases, auth tests, and negative scenarios</p>
          </div>
        </div>
      </header>

      <div className="tests-layout">
        <aside className="tests-form animate-in">
          <h3>API to test</h3>
          <label>
            Spec / description
            <textarea
              value={spec}
              onChange={(e) => setSpec(e.target.value)}
              placeholder="POST /api/orders — create order with items array"
              rows={3}
            />
          </label>
          <div className="form-row">
            <label>
              Method
              <select value={method} onChange={(e) => setMethod(e.target.value)}>
                {["GET", "POST", "PUT", "PATCH", "DELETE"].map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Count
              <input
                type="number"
                min={1}
                max={20}
                value={count}
                onChange={(e) => setCount(Number(e.target.value))}
              />
            </label>
          </div>
          <label>
            URL
            <input value={url} onChange={(e) => setUrl(e.target.value)} className="mono" />
          </label>
          <label>
            Body (optional)
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              className="mono"
              rows={4}
              placeholder='{"key": "value"}'
            />
          </label>

          <div className="demo-chips">
            <span className="chip-label">Quick demos:</span>
            {DEMO_SPECS.map((d) => (
              <button key={d.label} className="demo-chip" onClick={() => applyDemo(d)}>
                {d.label}
              </button>
            ))}
          </div>

          <button className="btn-generate" onClick={runGenerate} disabled={loading}>
            {loading ? (
              <>
                <Loader2 size={18} className="spin" />
                Generating…
              </>
            ) : (
              <>
                <Sparkles size={18} />
                Generate test cases
              </>
            )}
          </button>
          {error && <div className="error-banner">{error}</div>}
        </aside>

        <main className="tests-results animate-in" style={{ animationDelay: "80ms" }}>
          <div className="results-header">
            <h3>Generated tests</h3>
            {tests.length > 0 && (
              <span className={`llm-badge ${llmUsed ? "on" : "off"}`}>
                {llmUsed ? "OpenRouter LLM" : "Heuristic mode"}
              </span>
            )}
          </div>

          {loadingHistory ? (
            <div className="skeleton tests-skeleton" />
          ) : tests.length === 0 ? (
            <div className="tests-empty">
              <FlaskConical size={40} strokeWidth={1.2} />
              <p>Configure an API and generate test cases</p>
            </div>
          ) : (
            <div className="tests-grid">
              {tests.map((test, i) => (
                <article key={`${test.name}-${i}`} className={`test-card type-${test.test_type}`}>
                  <div className="test-card-head">
                    <span className={`method-badge method-${test.method.toLowerCase()}`}>
                      {test.method}
                    </span>
                    <span className="type-tag">{test.test_type}</span>
                  </div>
                  <h4>{test.name}</h4>
                  <p className="test-desc">{test.description}</p>
                  <code className="mono test-url">{test.url}</code>
                  {test.expected_status != null && (
                    <span className="expected">Expected: {test.expected_status}</span>
                  )}
                </article>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
