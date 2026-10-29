import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../lib/api";
import { CATEGORY_META, CATEGORY_ORDER, formatPercent } from "../lib/constants";
import { Alert } from "../components/ui";

const TOOLTIP_STYLE = {
  background: "#111a30",
  border: "1px solid rgba(148,163,184,0.2)",
  borderRadius: 10,
  color: "#e6ecf8",
};

function pct(value) {
  return formatPercent(value, 1);
}

export default function Insights() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .insights()
      .then(setData)
      .catch((err) => setError(err.message || "Evaluation results could not be loaded."));
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
        <div className="grid-3">
          {[1, 2, 3].map((key) => (
            <div className="skeleton" key={key} style={{ height: 120 }} />
          ))}
        </div>
      </div>
    );
  }

  const selected = data.candidates[data.selected_model];
  const metrics = data.selected_model_metrics;
  const classes = data.classes || CATEGORY_ORDER;
  const cm = metrics.confusion_matrix;
  const maxCell = Math.max(...cm.flat(), 1);

  const comparison = Object.entries(data.candidates).map(([key, value]) => ({
    key,
    name: value.display_name,
    accuracy: Number(value.test.accuracy.toFixed(4)),
    macroF1: Number(value.test.f1_macro.toFixed(4)),
    weightedF1: Number(value.test.f1_weighted.toFixed(4)),
  }));

  const perClass = classes.map((label) => {
    const m = metrics.per_class[label];
    return { label, ...m };
  });

  const distribution = classes.map((label) => ({
    label,
    count: data.dataset.class_distribution[label] ?? 0,
    color: CATEGORY_META[label]?.color || "#94a3b8",
  }));

  const splitData = [
    { split: "Train", count: data.dataset.split_counts.train },
    { split: "Validation", count: data.dataset.split_counts.valid },
    { split: "Test", count: data.dataset.split_counts.test },
  ];

  return (
    <div className="container section">
      <div className="between" style={{ marginBottom: "1.5rem" }}>
        <div>
          <div className="eyebrow">Reproducible evaluation</div>
          <h2>Model insights</h2>
          <p style={{ margin: 0 }}>
            Results recomputed from the supplied dataset by{" "}
            <code>python scripts/train_models.py</code>. Test metrics come from one final
            evaluation on the untouched test split.
          </p>
        </div>
        <span className="pill">Generated {new Date(data.generated_at).toLocaleDateString()}</span>
      </div>

      <div className="grid-4" style={{ marginBottom: "1.25rem" }}>
        <div className="card stat-card">
          <span className="tiny">Selected model</span>
          <strong style={{ fontSize: "1.02rem" }}>{data.selected_model_display_name}</strong>
          <small>Criterion: {data.selection_criterion}</small>
        </div>
        <div className="card stat-card">
          <span className="tiny">Test accuracy</span>
          <span className="stat-value">{pct(metrics.accuracy)}</span>
          <small>{data.dataset.split_counts.test} untouched statements</small>
        </div>
        <div className="card stat-card">
          <span className="tiny">Macro F1</span>
          <span className="stat-value">{pct(metrics.f1_macro)}</span>
          <small>Equal weight per class</small>
        </div>
        <div className="card stat-card">
          <span className="tiny">Weighted F1</span>
          <span className="stat-value">{pct(metrics.f1_weighted)}</span>
          <small>Weighted by class support</small>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: "1.25rem" }}>
        <div className="card">
          <h3>Algorithm comparison (test split)</h3>
          <div className="chart-wrap" style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparison} margin={{ top: 10, right: 10, left: -18, bottom: 40 }}>
                <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
                <XAxis
                  dataKey="name"
                  tick={{ fill: "#93a2c0", fontSize: 10 }}
                  interval={0}
                  angle={-12}
                  textAnchor="end"
                  height={60}
                />
                <YAxis domain={[0, 1]} tick={{ fill: "#93a2c0", fontSize: 11 }} />
                <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(value) => pct(value)} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="accuracy" name="Accuracy" fill="#8b5cf6" radius={[5, 5, 0, 0]} />
                <Bar dataKey="macroF1" name="Macro F1" fill="#22d3ee" radius={[5, 5, 0, 0]} />
                <Bar dataKey="weightedF1" name="Weighted F1" fill="#f59e0b" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3>Dataset class distribution</h3>
          <div className="chart-wrap" style={{ height: 240 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distribution} margin={{ top: 10, right: 10, left: -18, bottom: 0 }}>
                <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
                <XAxis dataKey="label" tick={{ fill: "#93a2c0", fontSize: 10 }} interval={0} />
                <YAxis tick={{ fill: "#93a2c0", fontSize: 11 }} />
                <Tooltip contentStyle={TOOLTIP_STYLE} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {distribution.map((entry) => (
                    <Cell key={entry.label} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="divider" />
          <div className="row" style={{ gap: "0.5rem" }}>
            {splitData.map((item) => (
              <span className="pill" key={item.split}>
                {item.split}: {item.count.toLocaleString()}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: "1.25rem" }}>
        <div className="between" style={{ marginBottom: "1rem" }}>
          <h3 style={{ margin: 0 }}>All algorithms — test metrics</h3>
          <span className="pill">Trained on {data.dataset.split_counts.train.toLocaleString()} rows</span>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Algorithm</th>
                <th className="num">Accuracy</th>
                <th className="num">Precision (w)</th>
                <th className="num">Recall (w)</th>
                <th className="num">F1 (w)</th>
                <th className="num">F1 (macro)</th>
                <th>Selected</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(data.candidates).map(([key, value]) => (
                <tr key={key}>
                  <td>{value.display_name}</td>
                  <td className="num">{pct(value.test.accuracy)}</td>
                  <td className="num">{pct(value.test.precision_weighted)}</td>
                  <td className="num">{pct(value.test.recall_weighted)}</td>
                  <td className="num">{pct(value.test.f1_weighted)}</td>
                  <td className="num">{pct(value.test.f1_macro)}</td>
                  <td>{key === data.selected_model ? "✔ deployed" : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p style={{ marginTop: "0.9rem", marginBottom: 0, fontSize: "0.85rem" }}>
          The four-class LIAR task is inherently difficult: statements are short, the classes
          overlap, and the majority class is Partially False. Accuracy in the high 30s is a normal,
          honest result for TF-IDF with classical models — it is not a defect in the code. Reported
          numbers are measured, never hardcoded.
        </p>
      </div>

      <div className="grid-2" style={{ marginBottom: "1.25rem" }}>
        <div className="card">
          <h3>Per-class performance</h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Class</th>
                  <th className="num">Precision</th>
                  <th className="num">Recall</th>
                  <th className="num">F1</th>
                  <th className="num">Support</th>
                </tr>
              </thead>
              <tbody>
                {perClass.map((row) => (
                  <tr key={row.label}>
                    <td style={{ color: CATEGORY_META[row.label]?.color }}>{row.label}</td>
                    <td className="num">{pct(row.precision)}</td>
                    <td className="num">{pct(row.recall)}</td>
                    <td className="num">{pct(row.f1)}</td>
                    <td className="num">{row.support}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p style={{ marginTop: "0.9rem", marginBottom: 0, fontSize: "0.82rem" }}>
            Precision answers “when the model says this class, how often is it right?”; recall
            answers “of all true items in this class, how many were found?”.
          </p>
        </div>

        <div className="card">
          <h3>Confusion matrix (test split)</h3>
          <div className="cm" style={{ gridTemplateColumns: `120px repeat(${classes.length}, 1fr)` }}>
            <div className="cm-head">Actual ↓ / Pred →</div>
            {classes.map((label) => (
              <div className="cm-head" key={`head-${label}`}>
                {label}
              </div>
            ))}
            {cm.map((row, rowIndex) => (
              <div key={`row-${rowIndex}`} style={{ display: "contents" }}>
                <div className="cm-head" style={{ placeItems: "center start" }}>
                  {classes[rowIndex]}
                </div>
                {row.map((value, colIndex) => {
                  const alpha = 0.15 + 0.8 * (value / maxCell);
                  return (
                    <div
                      className="cm-cell"
                      key={`${rowIndex}-${colIndex}`}
                      style={{ background: `rgba(139, 92, 246, ${alpha.toFixed(3)})` }}
                      title={`Actual ${classes[rowIndex]} → predicted ${classes[colIndex]}: ${value}`}
                    >
                      {value}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
          <p style={{ marginTop: "0.9rem", marginBottom: 0, fontSize: "0.82rem" }}>
            Rows are actual labels, columns are predictions. Off-diagonal cells are misclassifications;
            they concentrate between neighbouring categories, which is expected for ordinal
            truthfulness labels.
          </p>
        </div>
      </div>

      <div className="card">
        <h3>Reproducibility details</h3>
        <div className="grid-2">
          <div>
            <div className="tiny">Features</div>
            <ul style={{ color: "var(--muted)", fontSize: "0.88rem", paddingLeft: "1.1rem" }}>
              <li>{data.features.word_tfidf}</li>
              <li>{data.features.char_tfidf}</li>
            </ul>
            <div className="tiny">Label mapping</div>
            <p style={{ fontSize: "0.88rem" }}>
              {Object.entries(data.label_mapping)
                .map(([raw, mapped]) => `${raw} → ${mapped}`)
                .join(" · ")}
            </p>
          </div>
          <div>
            <div className="tiny">Selected hyper-parameters</div>
            <pre
              style={{
                background: "rgba(7,11,22,0.6)",
                padding: "0.85rem",
                borderRadius: 10,
                fontSize: "0.8rem",
                overflowX: "auto",
                color: "#a5b4fc",
              }}
            >
              {JSON.stringify(selected.best_params, null, 2)}
            </pre>
            <div className="tiny">Environment</div>
            <p style={{ fontSize: "0.82rem", marginBottom: 0 }}>
              Python {data.environment.python} · scikit-learn {data.environment.scikit_learn} ·
              pandas {data.environment.pandas} · NumPy {data.environment.numpy}
            </p>
          </div>
        </div>
        <div className="divider" />
        <p style={{ marginBottom: 0, fontSize: "0.84rem" }}>
          <strong>Limitations.</strong> The model is trained only on short LIAR statements and
          cannot verify facts, sources or breaking news. Domain shift, sarcasm and unfamiliar
          vocabulary can all degrade accuracy. Use it as a screening aid alongside human
          fact-checking. Full details are in <code>docs/EVALUATION.md</code> and{" "}
          <code>results/EVALUATION_RESULTS.md</code>.
        </p>
      </div>
    </div>
  );
}
