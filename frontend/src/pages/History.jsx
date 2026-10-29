import { useCallback, useEffect, useState } from "react";
import { api } from "../lib/api";
import { formatDate, formatPercent } from "../lib/constants";
import { Alert, EmptyState, LabelBadge } from "../components/ui";

const PAGE_SIZE = 10;

export default function History() {
  const [data, setData] = useState(null);
  const [page, setPage] = useState(0);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busyId, setBusyId] = useState(null);

  const load = useCallback(() => {
    setError("");
    api
      .history(PAGE_SIZE, page * PAGE_SIZE)
      .then(setData)
      .catch((err) => setError(err.message));
  }, [page]);

  useEffect(load, [load]);

  async function removeOne(id) {
    if (!window.confirm("Delete this prediction from your history?")) return;
    setBusyId(id);
    try {
      await api.deletePrediction(id);
      setNotice("Prediction deleted.");
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  }

  async function clearAll() {
    if (!window.confirm("Delete your entire prediction history? This cannot be undone.")) return;
    try {
      const response = await api.clearHistory();
      setNotice(`${response.deleted} predictions deleted.`);
      setPage(0);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  const total = data?.total ?? 0;
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="container section">
      <div className="between" style={{ marginBottom: "1.5rem" }}>
        <div>
          <div className="eyebrow">Your records</div>
          <h2>Prediction history</h2>
          <p style={{ margin: 0 }}>{total} saved prediction{total === 1 ? "" : "s"}.</p>
        </div>
        {total > 0 && (
          <button type="button" className="btn btn-danger btn-sm" onClick={clearAll}>
            Clear history
          </button>
        )}
      </div>

      <Alert>{error}</Alert>
      <Alert type="success">{notice}</Alert>

      {!data && !error && <div className="skeleton" style={{ height: 220 }} />}

      {data && total === 0 && (
        <EmptyState title="No predictions saved">
          <p>Your prediction history is private to your account and will appear here.</p>
        </EmptyState>
      )}

      {data && total > 0 && (
        <>
          <ul className="list-reset stack">
            {data.items.map((item) => (
              <li className="history-item" key={item.id}>
                <div className="between">
                  <div className="row" style={{ gap: "0.5rem" }}>
                    <LabelBadge label={item.label} score={item.confidence} />
                    <span className="pill">{item.model_name}</span>
                    {item.confidence !== null && (
                      <span className="pill">
                        {formatPercent(item.confidence)} confidence
                      </span>
                    )}
                  </div>
                  <div className="row" style={{ gap: "0.75rem" }}>
                    <span className="muted tiny">{formatDate(item.created_at)}</span>
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      onClick={() => removeOne(item.id)}
                      disabled={busyId === item.id}
                    >
                      {busyId === item.id ? "Deleting…" : "Delete"}
                    </button>
                  </div>
                </div>
                <p style={{ margin: 0 }}>{item.text}</p>
              </li>
            ))}
          </ul>

          <div className="between" style={{ marginTop: "1.25rem" }}>
            <span className="muted" style={{ fontSize: "0.85rem" }}>
              Page {page + 1} of {pages}
            </span>
            <div className="row" style={{ gap: "0.5rem" }}>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setPage((value) => Math.max(0, value - 1))}
                disabled={page === 0}
              >
                Previous
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setPage((value) => Math.min(pages - 1, value + 1))}
                disabled={page >= pages - 1}
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
