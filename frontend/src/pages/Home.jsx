import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import { CATEGORY_META, CATEGORY_ORDER, formatPercent } from "../lib/constants";

const STEPS = [
  {
    n: "01",
    title: "Enter a claim",
    text: "Paste a statement, headline or short article excerpt into the detection page.",
  },
  {
    n: "02",
    title: "Text is normalised",
    text: "URLs, HTML, punctuation and digits are removed; the same cleaning used in training is applied.",
  },
  {
    n: "03",
    title: "TF-IDF features",
    text: "Word (1–2 gram) and character (3–5 gram) TF-IDF vectors are extracted by the saved pipeline.",
  },
  {
    n: "04",
    title: "Model estimates a category",
    text: "The selected classifier returns one of four reliability levels with its class scores.",
  },
];

export default function Home() {
  const { isAuthenticated } = useAuth();
  const [health, setHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ model_ready: false }));
    api
      .insights()
      .then((data) => setMetrics(data))
      .catch(() => setMetrics(null));
  }, []);

  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <div className="eyebrow">Machine Learning · NLP · Four-level classification</div>
            <h1>
              Read between the <span style={{ color: "var(--violet)" }}>headlines</span>.
            </h1>
            <p className="lead">
              TruthLens AI classifies a news claim into one of four reliability levels —{" "}
              <strong>Real</strong>, <strong>Misleading</strong>, <strong>Partially False</strong> and{" "}
              <strong>Fake</strong> — using TF-IDF text features and classical machine-learning models
              trained on the LIAR benchmark dataset.
            </p>
            <div className="row" style={{ marginTop: "1.5rem" }}>
              <Link to={isAuthenticated ? "/detect" : "/register"} className="btn btn-primary">
                {isAuthenticated ? "Analyse a claim" : "Get started free"}
              </Link>
              <Link to={isAuthenticated ? "/dashboard" : "/login"} className="btn btn-secondary">
                {isAuthenticated ? "Go to dashboard" : "Login"}
              </Link>
            </div>
            <div className="row" style={{ marginTop: "1.5rem", gap: "0.6rem" }}>
              <span className="pill">
                <span
                  className="dot"
                  style={{ background: health?.model_ready ? "var(--green)" : "var(--red)" }}
                />
                {health === null
                  ? "Checking model…"
                  : health.model_ready
                    ? "Model loaded and ready"
                    : "Model not trained yet"}
              </span>
              {metrics && (
                <span className="pill">
                  Selected: {metrics.selected_model_display_name}
                </span>
              )}
              {metrics?.selected_model_metrics && (
                <span className="pill">
                  Test accuracy {formatPercent(metrics.selected_model_metrics.accuracy)}
                </span>
              )}
            </div>
          </div>

          <div className="hero-visual">
            <div className="orb orb-one" />
            <div className="orb orb-two" />
            <div className="card hero-card">
              <div className="scan-line" />
              <div className="tiny">Example model output</div>
              <h3 style={{ marginTop: 4 }}>“The new policy will reduce taxes for every household.”</h3>
              <div className="stack" style={{ marginTop: "1rem", gap: "0.7rem" }}>
                {CATEGORY_ORDER.map((label, index) => {
                  const widths = [16, 24, 41, 19];
                  return (
                    <div key={label}>
                      <div className="between" style={{ marginBottom: 4 }}>
                        <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>{label}</span>
                        <span className="muted tiny">{widths[index]}%</span>
                      </div>
                      <div className="score-track">
                        <div
                          className="score-fill"
                          style={{
                            width: `${widths[index]}%`,
                            background: CATEGORY_META[label].color,
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
              <p className="tiny" style={{ marginTop: "1rem", marginBottom: 0 }}>
                Illustrative layout only — open the detection page to run the real trained model.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="between" style={{ marginBottom: "1.5rem" }}>
            <div>
              <div className="eyebrow">How it works</div>
              <h2>From raw text to a reliability estimate</h2>
            </div>
            <Link to="/insights" className="btn btn-ghost btn-sm">
              See measured results
            </Link>
          </div>
          <div className="grid-4">
            {STEPS.map((step) => (
              <div className="card card-tight" key={step.n}>
                <div className="tiny" style={{ color: "var(--cyan)" }}>
                  {step.n}
                </div>
                <h3 style={{ marginTop: 6 }}>{step.title}</h3>
                <p style={{ margin: 0, fontSize: "0.9rem" }}>{step.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="eyebrow">The four categories</div>
          <h2 style={{ marginBottom: "1.5rem" }}>A more useful answer than true or false</h2>
          <div className="grid-4">
            {CATEGORY_ORDER.map((label) => {
              const meta = CATEGORY_META[label];
              return (
                <div className="card" key={label} style={{ borderColor: `${meta.color}44` }}>
                  <span className="badge" style={{ background: meta.soft, color: meta.color }}>
                    <span className="dot" style={{ background: meta.color }} />
                    {label}
                  </span>
                  <p style={{ marginTop: "0.9rem", marginBottom: 0, fontSize: "0.92rem" }}>
                    {meta.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container grid-2">
          <div className="card">
            <div className="eyebrow">The methods</div>
            <h2>Four classical algorithms, one fair protocol</h2>
            <ul style={{ color: "var(--muted)", paddingLeft: "1.2rem", marginBottom: 0 }}>
              <li>
                <strong>Logistic Regression (A1)</strong> — linear, interpretable baseline.
              </li>
              <li>
                <strong>Support Vector Machine (A2)</strong> — maximum-margin linear classifier on
                sparse TF-IDF features.
              </li>
              <li>
                <strong>Random Forest (A3)</strong> — non-linear tree ensemble.
              </li>
              <li>
                <strong>Multinomial Naive Bayes (A4)</strong> — fast probabilistic baseline for text.
              </li>
            </ul>
            <p style={{ marginTop: "1rem", marginBottom: 0, fontSize: "0.9rem" }}>
              All four share the same preprocessing, features, training split and evaluation
              metrics. The deployed model is chosen by validation macro-F1 and evaluated once on
              the untouched test split.
            </p>
          </div>

          <div className="card">
            <div className="eyebrow">Responsible use</div>
            <h2>What this system can and cannot do</h2>
            <p>
              The model learns linguistic patterns from short, fact-checked political statements
              (the LIAR dataset). It does not browse the web, query fact-checkers or verify evidence
              in real time.
            </p>
            <div className="alert alert-info">
              A prediction is a <strong>statistical estimate</strong>, not proof. Never treat the
              output as a verdict on a real person or organisation — verify with primary sources and
              professional fact-checkers.
            </div>
            <div className="divider" />
            <div className="tiny">Label mapping used in training</div>
            <p style={{ margin: "0.4rem 0 0", fontSize: "0.86rem" }}>
              true → Real · mostly-true → Misleading · half-true &amp; barely-true → Partially False ·
              false &amp; pants-fire → Fake
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
