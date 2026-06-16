import { useEffect, useState } from "react";
import { BarChart3, Bot, History, TestTube2 } from "lucide-react";
import Dashboard from "./components/Dashboard";
import DebugPanel from "./components/DebugPanel";
import HistoryPanel from "./components/HistoryPanel";
import TestsPanel from "./components/TestsPanel";
import "./App.css";

type Tab = "analytics" | "debug" | "tests" | "history";

function tabFromHash(): Tab {
  const hash = window.location.hash.replace("#", "");
  if (hash === "debug") return "debug";
  if (hash === "tests") return "tests";
  if (hash === "history") return "history";
  return "analytics";
}

export default function App() {
  const [tab, setTab] = useState<Tab>(tabFromHash);

  useEffect(() => {
    const sync = () => setTab(tabFromHash());
    window.addEventListener("hashchange", sync);
    return () => window.removeEventListener("hashchange", sync);
  }, []);

  const goTo = (next: Tab) => {
    setTab(next);
    window.location.hash = next === "analytics" ? "#analytics" : `#${next}`;
  };

  return (
    <div className="app-shell">
      <nav className="app-nav">
        <div className="nav-brand">AI API Debugger</div>
        <div className="nav-tabs">
          <button
            className={`nav-tab ${tab === "analytics" ? "active" : ""}`}
            onClick={() => goTo("analytics")}
          >
            <BarChart3 size={16} />
            Analytics
          </button>
          <button
            className={`nav-tab ${tab === "debug" ? "active" : ""}`}
            onClick={() => goTo("debug")}
          >
            <Bot size={16} />
            AI Debugger
          </button>
          <button
            className={`nav-tab ${tab === "tests" ? "active" : ""}`}
            onClick={() => goTo("tests")}
          >
            <TestTube2 size={16} />
            Tests
          </button>
          <button
            className={`nav-tab ${tab === "history" ? "active" : ""}`}
            onClick={() => goTo("history")}
          >
            <History size={16} />
            History
          </button>
        </div>
        <a
          className="nav-link"
          href={`${import.meta.env.VITE_API_URL ? (import.meta.env.VITE_API_URL.startsWith("http") ? import.meta.env.VITE_API_URL : `https://${import.meta.env.VITE_API_URL}`) : "http://localhost:8010"}/docs`}
          target="_blank"
          rel="noreferrer"
        >
          API Docs
        </a>
      </nav>
      <main>
        {tab === "analytics" && <Dashboard onOpenDebugger={() => goTo("debug")} />}
        {tab === "debug" && <DebugPanel />}
        {tab === "tests" && <TestsPanel />}
        {tab === "history" && <HistoryPanel />}
      </main>
    </div>
  );
}
