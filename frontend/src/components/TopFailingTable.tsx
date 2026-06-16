import { Fragment, useState } from "react";
import { ChevronDown, ChevronRight, ExternalLink } from "lucide-react";
import type { TopFailingEndpoint } from "../types/analytics";
import { shortUrl } from "./Charts";

export default function TopFailingTable({ data }: { data: TopFailingEndpoint[] }) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (!data.length) {
    return (
      <div className="table-empty">
        <span className="success-badge">All clear</span>
        <p>No failing endpoints in this period</p>
      </div>
    );
  }

  return (
    <div className="failing-table-wrap">
      <table className="failing-table">
        <thead>
          <tr>
            <th></th>
            <th>Endpoint</th>
            <th>Method</th>
            <th>Failures</th>
            <th>Last seen</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => {
            const key = `${row.method}:${row.url}`;
            const isOpen = expanded === key;
            return (
              <Fragment key={key}>
                <tr
                  className={`failing-row ${isOpen ? "open" : ""}`}
                  onClick={() => setExpanded(isOpen ? null : key)}
                >
                  <td className="chevron">
                    {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                  </td>
                  <td className="url-cell">
                    <span className="mono" title={row.url}>
                      {shortUrl(row.url)}
                    </span>
                    <a href={row.url} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}>
                      <ExternalLink size={12} />
                    </a>
                  </td>
                  <td>
                    <span className={`method-badge method-${row.method.toLowerCase()}`}>{row.method}</span>
                  </td>
                  <td>
                    <span className="fail-count">{row.failure_count}</span>
                  </td>
                  <td className="muted">
                    {row.last_seen
                      ? new Date(row.last_seen).toLocaleString(undefined, {
                          month: "short",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })
                      : "—"}
                  </td>
                </tr>
                {isOpen && row.last_error && (
                  <tr className="error-detail-row">
                    <td colSpan={5}>
                      <pre className="error-pre mono">{row.last_error}</pre>
                    </td>
                  </tr>
                )}
              </Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
