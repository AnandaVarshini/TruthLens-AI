import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../lib/api";
import { CATEGORY_META, CATEGORY_ORDER, formatDate, formatPercent } from "../lib/constants";
import { Alert, EmptyState, LabelBadge } from "../components/ui";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .stats()
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="container section">
        <Alert>{error}</Alert>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="container section">
        <div className="skeleton" style={{ height: 120, marginBottom: 18 }} />
        <div className="grid-4">
          {[1, 2, 3, 4].map((key) => (
            <div className="skeleton" key={key} style={{ height: 110 }} />
          ))}
        </div>
      </div>
    );
  }

  const chartData = data.counts_by_label.map((item) => ({
    label: item.label,
    count: item.count,
    color: CATEGORY_META[item.label]?.color || "#94a3b8",
  }));
  const hasHistory = data.total_predictions > 0;

  return (
    <div className="container section">
      <div className="between" style={{ marginBottom: "1.5rem" }}>
        <div>
          <div className="eyebrow">Your workspace</div>
          <h2>Dashboard</h2>
          <p style={{ margin: 0 }}>
            Activity computed from your saved predictions — nothing here is simulated.
          </p>
        </div>
        <Link to="/detect" className="btn btn-primary">
          Analyse a new claim
        </Link>
      </div>

      <div className="grid-4" style={{ marginBottom: "1.25rem" }}>
        <div className="card stat-card">
          <span className="tiny">Total predictions</span>
          <span className="stat-value">{data.total_predictions}</span>
          <small>Saved to your account</small>
        </div>
        {CATEGORY_ORDER.map((label) => {
          const item = data.counts_by_label.find((entry) => entry.label === label);
          return (
            <div className="card stat-card" key={label}>
              <span className="tiny" style={{ color: CATEGORY_META[label].color }}>
                {label}
              </span>
              <span className="stat-value">{item?.count ?? 0}</span>
              <small>Predictions in this category</small>
            </div>
          );
        })}
      </div>

      <div className="grid-2" style={{ marginBottom: "1.25rem" }}>
        <div className="card">
          <div className="between" style={{ marginBottom: 10 }}>
            <h3 style={{ margin: 0 }}>Predictions by category</h3>
            <span className="pill">{data.model_name}</span>
          </div>
          {hasHistory ? (
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
                  <XAxis dataKey="label" tick={{ fill: "#93a2c0", fontSize: 11 }} interval={0} />
                  <YAxis allowDecimals={false} tick={{ fill: "#93a2c0", fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{
                      background: "#111a30",
                      border: "1px solid rgba(148,163,184,0.2)",
                      borderRadius: 10,
                      color: "#e6ecf8",
                    }}
                  />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {chartData.map((entry) => (
                      <Cell key={entry.label} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState title="No chart yet">
              <p style={{ margin: 0 }}>Your category chart will appear after your first prediction.</p>
            </EmptyState>
          )}
        </div>

        <div className="card">
          <h3>Selected model</h3>
          <p style={{ marginBottom: "0.75rem" }}>{data.model_name}</p>
          <div className="row">
            <span className="pill">
              Test accuracy {formatPercent(data.model_accuracy_test)}
            </span>
            <Link to="/insights" className="pill">
              Full evaluation →
            </Link>
          </div>
          <div className="divider" />
          <p style={{ fontSize: "0.85rem", marginBottom: 0 }}>
            Metrics come from a single evaluation on the untouched LIAR test split. They describe
            the model, not the correctness of any individual prediction.
          </p>
        </div>
      </div>

      <div className="card">
        <div className="between" style={{ marginBottom: "1rem" }}>
          <h3 style={{ margin: 0 }}>Recent predictions</h3>
          {hasHistory && (
            <Link to="/history" className="btn btn-ghost btn-sm">
              View all
            </Link>
          )}
        </div>
        {data.recent.length === 0 ? (
          <EmptyState title="No predictions yet">
            <p>Enter a claim on the detection page to create your first record.</p>
            <Link to="/detect" className="btn btn-primary btn-sm">
              Go to detection
            </Link>
          </EmptyState>
        ) : (
          <ul className="list-reset stack">
            {data.recent.map((item) => (
              <li className="history-item" key={item.id}>
                <div className="between">
                  <LabelBadge label={item.label} score={item.confidence} />
                  <span className="muted tiny">{formatDate(item.created_at)}</span>
                </div>
                <p className="clamp-2" style={{ margin: 0 }}>
                  {item.text}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
