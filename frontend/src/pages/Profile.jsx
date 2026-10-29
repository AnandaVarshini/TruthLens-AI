import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/AuthContext";
import { formatDate } from "../lib/constants";

export default function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="container section">
      <div className="eyebrow">Account</div>
      <h2>Profile</h2>

      <div className="grid-2" style={{ marginTop: "1.5rem" }}>
        <div className="card">
          <h3>Your details</h3>
          <div className="stack" style={{ gap: "0.9rem", marginTop: "1rem" }}>
            <div>
              <div className="tiny">Name</div>
              <div>{user?.name}</div>
            </div>
            <div>
              <div className="tiny">Email</div>
              <div>{user?.email}</div>
            </div>
            <div>
              <div className="tiny">Member since</div>
              <div>{formatDate(user?.created_at)}</div>
            </div>
            <div></div>
            <div className="row">
              <Link to="/dashboard" className="btn btn-secondary btn-sm">
                Dashboard
              </Link>
              <Link to="/history" className="btn btn-ghost btn-sm">
                My history
              </Link>
              <button type="button" className="btn btn-danger btn-sm" onClick={handleLogout}>
                Log out
              </button>
            </div>
          </div>
        </div>

        <div className="card">
          <h3>Privacy and security</h3>
          <ul style={{ color: "var(--muted)", fontSize: "0.9rem", paddingLeft: "1.1rem" }}>
            <li>Passwords are hashed with bcrypt and never stored or returned in plain text.</li>
            <li>
              Sessions use signed JWT access tokens; protected API endpoints reject requests
              without a valid token.
            </li>
            <li>Prediction history is scoped to your account and cannot be read by other users.</li>
            <li>You can delete individual predictions or clear your entire history.</li>
          </ul>
          <div className="alert alert-info">
            Logging out removes the token from this browser. Always log out on shared computers.
          </div>
        </div>
      </div>
    </div>
  );
}
