import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuth } from "../lib/AuthContext";

const PUBLIC_LINKS = [
  { to: "/", label: "Home" },
  { to: "/insights", label: "Model Insights" },
];

const PRIVATE_LINKS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/detect", label: "Detect" },
  { to: "/history", label: "History" },
  { to: "/insights", label: "Model Insights" },
];

export default function Layout() {
  const { isAuthenticated, logout, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);

  useEffect(() => setOpen(false), [location.pathname]);

  const links = isAuthenticated ? PRIVATE_LINKS : PUBLIC_LINKS;

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <>
      <header className="nav">
        <div className="container nav-inner">
          <Link to="/" className="brand" aria-label="TruthLens AI home">
            <span className="brand-mark">TL</span>
            <span>
              TruthLens AI
              <small>Fake News Detection</small>
            </span>
          </Link>

          <nav className={`nav-links ${open ? "open" : ""}`} aria-label="Main navigation">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.to === "/"}
                className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
              >
                {link.label}
              </NavLink>
            ))}
            {isAuthenticated ? (
              <>
                <NavLink to="/profile" className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
                  {user?.name?.split(" ")[0] || "Profile"}
                </NavLink>
                <button type="button" className="btn btn-ghost btn-sm" onClick={handleLogout}>
                  Log out
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" className="nav-link">
                  Login
                </NavLink>
                <Link to="/register" className="btn btn-primary btn-sm">
                  Get started
                </Link>
              </>
            )}
          </nav>

          <button
            type="button"
            className="nav-toggle"
            aria-label="Toggle navigation"
            aria-expanded={open}
            onClick={() => setOpen((value) => !value)}
          >
            ☰
          </button>
        </div>
      </header>

      <main>
        <Outlet />
      </main>

      <footer className="footer">
        <div className="container between">
          <div>
            <strong>TruthLens AI</strong> — Fake News Detection System Using Machine Learning
            <div className="tiny" style={{ marginTop: 6 }}>
              Four-class LIAR classification · TF-IDF · Logistic Regression, SVM, Random Forest, Naive Bayes
            </div>
          </div>
          <div className="tiny">
            Predictions are statistical estimates, not proof of truth. Always verify with primary sources.
          </div>
        </div>
      </footer>
    </>
  );
}
