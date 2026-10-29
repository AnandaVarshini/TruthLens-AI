import { useState } from "react";
import { api } from "../lib/api";
import { CATEGORY_META, CATEGORY_ORDER, formatDate, formatPercent } from "../lib/constants";
import { Alert, ScoreBars, Spinner } from "../components/ui";

const MAX_CHARS = 5000;
const EXAMPLES = [
  "The new healthcare policy will reduce premiums for every family in the country by half.",
  "Scientists have confirmed that drinking seawater cures all known viral infections.",
  "Unemployment fell last month, according to the latest labour department report.",
];

export default function Detect() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const meta = result ? CATEGORY_META[result.label] : null;

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    if (!text.trim()) {
      setError("Please enter a news claim before requesting a prediction.");
      return;
    }
    if (text.trim().length < 10) {
      setError("The statement is too short to analyse (minimum 10 characters).");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const response = await api.predict(text);
      setResult(response);
    } catch (err) {
      setError(err.message || "The prediction could not be completed.");
    } finally {
      setLoading(false);
    }
  }

  function clearAll() {
    setText("");
    setResult(null);
    setError("");
  }

  return (
    <div className="container section">
      <div className="between" style={{ marginBottom: "1.5rem" }}>
        <div>
          <div className="eyebrow">Step 2</div>
          <h2>Fake news detection</h2>
          <p style={{ margin: 0 }}>
            Submit a claim to the trained model. The result is a model estimate, not a fact-check.
          </p>
        </div>
        <span className="pill">Four-class classifier</span>
      </div>

      <div className="grid-2">
        <div className="card">
          <form className="form" onSubmit={handleSubmit}>
            <div className="field">
              <label className="label" htmlFor="claim">
                News claim or statement
              </label>
              <textarea
                id="claim"
                className="textarea"
                maxLength={MAX_CHARS}
                placeholder="Paste a statement, headline or short excerpt here…"
                value={text}
                onChange={(event) => setText(event.target.value)}
              />
              <div className="between">
                <small>
                  {text.length} / {MAX_CHARS} characters
                </small>
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={() => setText(EXAMPLES[0])}
                >
                  Use an example
                </button>
              </div>
            </div>

            <Alert>{error}</Alert>

            <div className="row">
              <button type="submit" className="btn btn-primary" disabled={loading || !text.trim()}>
                {loading ? <Spinner label="Analysing…" /> : "Predict category"}
              </button>
              <button type="button" className="btn btn-ghost" onClick={clearAll} disabled={loading}>
                Clear
              </button>
            </div>
            <p style={{ fontSize: "0.8rem", margin: 0 }}>
              The text is cleaned with the exact preprocessing used in training, then passed to the
              saved TF-IDF + classifier pipeline. Nothing is sent to a third-party service.
            </p>
          </form>
        </div>

        <div className="stack">
          {loading && (
            <div className="card">
              <div className="skeleton" style={{ height: 22, width: "50%", marginBottom: 12 }} />
              <div className="skeleton" style={{ height: 70 }} />
            </div>
          )}

          {!result && !loading && (
            <div className="card">
              <h3>What you will see</h3>
              <ul style={{ color: "var(--muted)", paddingLeft: "1.2rem" }}>
                <li>The predicted category with its colour code</li>
                <li>Class scores for all four categories</li>
                <li>The model name and the prediction timestamp</li>
                <li>A short explanation of what the output means</li>
              </ul>
              <div className="alert alert-info" style={{ marginTop: "0.75rem" }}>
                Each category is one of: Real, Misleading, Partially False, Fake.
              </div>
            </div>
          )}

          {result && (
            <>
              <div
                className="result-banner"
                style={{
                  background: meta.soft,
                  borderColor: `${meta.color}66`,
                }}
              >
                <span className="tiny" style={{ color: meta.color }}>
                  Predicted category
                </span>
                <span className="result-label" style={{ color: meta.color }}>
                  {result.label}
                </span>
                <p style={{ margin: 0, color: "var(--text)" }}>{meta.description}</p>
                <div className="row" style={{ gap: "0.5rem", marginTop: 4 }}>
                  {result.confidence !== null && (
                    <span className="pill">
                      {result.score_type === "probability"
                        ? "Model probability"
                        : "Relative score"}{" "}
                      {formatPercent(result.confidence)}
                    </span>
                  )}
                  <span className="pill">{result.model_name}</span>
                  <span className="pill">{formatDate(result.created_at)}</span>
                </div>
              </div>

              <div className="card">
                <div className="between" style={{ marginBottom: "1rem" }}>
                  <h3 style={{ margin: 0 }}>Class scores</h3>
                  <span className="pill">
                    {result.score_type === "probability" ? "Probabilities" : "Decision scores"}
                  </span>
                </div>
                <ScoreBars scores={result.scores} scoreType={result.score_type} />
                <div className="divider" />
                <p style={{ fontSize: "0.82rem", marginBottom: 0 }}>
                  The model compares the wording of your claim with patterns learned from{" "}
                  {"LIAR"} statements. It does not check facts, sources or current events. A low
                  score for a category does not by itself prove the claim is correct.
                </p>
              </div>

              <div className="card card-tight">
                <div className="tiny" style={{ marginBottom: 6 }}>
                  Category reference
                </div>
                <div className="row" style={{ gap: "0.4rem" }}>
                  {CATEGORY_ORDER.map((label) => (
                    <span
                      key={label}
                      className="badge"
                      style={{
                        background: CATEGORY_META[label].soft,
                        color: CATEGORY_META[label].color,
                        opacity: label === result.label ? 1 : 0.55,
                      }}
                    >
                      {label}
                    </span>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
