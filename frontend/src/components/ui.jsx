import { CATEGORY_META } from "../lib/constants";

export function LabelBadge({ label, score }) {
  const meta = CATEGORY_META[label] || { color: "#94a3b8", soft: "rgba(148,163,184,0.15)" };
  return (
    <span className="badge" style={{ background: meta.soft, color: meta.color }}>
      <span className="dot" style={{ background: meta.color }} />
      {label}
      {score !== undefined && score !== null ? ` · ${(score * 100).toFixed(1)}%` : ""}
    </span>
  );
}

export function ScoreBars({ scores, scoreType }) {
  if (!scores?.length) return null;
  const isProbability = scoreType === "probability";
  return (
    <div className="stack" style={{ gap: "0.7rem" }}>
      {scores.map((item) => {
        const meta = CATEGORY_META[item.label] || { color: "#94a3b8" };
        return (
          <div key={item.label}>
            <div className="between" style={{ marginBottom: 4 }}>
              <span style={{ fontSize: "0.88rem", fontWeight: 600 }}>{item.label}</span>
              <span className="muted" style={{ fontSize: "0.82rem" }}>
                {(item.score * 100).toFixed(1)}%
              </span>
            </div>
            <div className="score-track">
              <div
                className="score-fill"
                style={{ width: `${Math.max(2, item.score * 100)}%`, background: meta.color }}
              />
            </div>
          </div>
        );
      })}
      {!isProbability && (
        <p style={{ margin: 0, fontSize: "0.78rem" }}>
          This model does not produce calibrated probabilities. The bars show normalised decision
          scores and should be read as relative model confidence, not as a probability that the
          claim is true.
        </p>
      )}
    </div>
  );
}

export function Alert({ type = "error", children }) {
  if (!children) return null;
  return <div className={`alert alert-${type}`}>{children}</div>;
}

export function Spinner({ label }) {
  return (
    <span className="row" style={{ gap: 8 }}>
      <span className="spinner" />
      {label ? <span>{label}</span> : null}
    </span>
  );
}

export function EmptyState({ title, children }) {
  return (
    <div className="empty">
      <h3>{title}</h3>
      {children}
    </div>
  );
}
