import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/AuthContext";
import { Alert, Spinner } from "../components/ui";

const INITIAL = { name: "", email: "", password: "", confirm_password: "" };

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(INITIAL);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update(field) {
    return (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));
  }

  function validate() {
    if (form.name.trim().length < 2) return "Please enter your full name.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) return "Please enter a valid email address.";
    if (form.password.length < 8) return "The password must be at least 8 characters long.";
    if (form.password !== form.confirm_password) return "The passwords do not match.";
    return "";
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const message = validate();
    if (message) {
      setError(message);
      return;
    }
    setError("");
    setSubmitting(true);
    try {
      await register({
        name: form.name.trim(),
        email: form.email.trim(),
        password: form.password,
        confirm_password: form.confirm_password,
      });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message || "Registration failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="container auth-shell">
      <div className="card auth-card">
        <div className="eyebrow">Create an account</div>
        <h2>Start using TruthLens AI</h2>
        <p style={{ fontSize: "0.92rem" }}>
          Your password is hashed on the server and is never stored in plain text.
        </p>
        <form className="form" onSubmit={handleSubmit} noValidate>
          <Alert>{error}</Alert>
          <div className="field">
            <label className="label" htmlFor="name">
              Full name
            </label>
            <input
              id="name"
              className="input"
              autoComplete="name"
              placeholder="Your name"
              value={form.name}
              onChange={update("name")}
              required
            />
          </div>
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
          <div className="grid-2" style={{ gap: "1rem" }}>
            <div className="field">
              <label className="label" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                className="input"
                autoComplete="new-password"
                placeholder="At least 8 characters"
                value={form.password}
                onChange={update("password")}
                required
              />
            </div>
            <div className="field">
              <label className="label" htmlFor="confirm_password">
                Confirm password
              </label>
              <input
                id="confirm_password"
                type="password"
                className="input"
                autoComplete="new-password"
                placeholder="Repeat password"
                value={form.confirm_password}
                onChange={update("confirm_password")}
                required
              />
            </div>
          </div>
          <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
            {submitting ? <Spinner label="Creating account…" /> : "Create account"}
          </button>
        </form>
        <div className="divider" />
        <p style={{ margin: 0, fontSize: "0.9rem" }}>
          Already registered? <Link to="/login" style={{ color: "var(--violet)" }}>Log in</Link>
        </p>
      </div>
    </div>
  );
}
