import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/AuthContext";
import { Alert, Spinner } from "../components/ui";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update(field) {
    return (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    if (!form.email.trim() || !form.password) {
      setError("Please enter both your email and password.");
      return;
    }
    setSubmitting(true);
    try {
      await login(form.email.trim(), form.password);
      navigate(location.state?.from || "/dashboard", { replace: true });
    } catch (err) {
      setError(err.message || "Login failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="container auth-shell">
      <div className="card auth-card">
        <div className="eyebrow">Welcome back</div>
        <h2>Log in to TruthLens AI</h2>
        <p style={{ fontSize: "0.92rem" }}>
          Access your dashboard, run predictions and review your history.
        </p>
        <form className="form" onSubmit={handleSubmit} noValidate>
          <Alert>{error}</Alert>
          <div className="field">
            <label className="label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="input"
              autoComplete="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={update("email")}
              required
            />
          </div>
          <div className="field">
            <label className="label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="input"
              autoComplete="current-password"
              placeholder="Your password"
              value={form.password}
              onChange={update("password")}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
            {submitting ? <Spinner label="Signing in…" /> : "Log in"}
          </button>
        </form>
        <div className="divider" />
        <p style={{ margin: 0, fontSize: "0.9rem" }}>
          New here? <Link to="/register" style={{ color: "var(--violet)" }}>Create an account</Link>
        </p>
      </div>
    </div>
  );
}
