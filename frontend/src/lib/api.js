export const API_BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function authHeaders() {
  const token = localStorage.getItem("truthlens_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json", ...(auth ? authHeaders() : {}) };
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(
      "Cannot reach the backend. Make sure it is running on http://localhost:8000.",
      0
    );
  }

  if (response.status === 204) return null;

  let payload = null;
  const text = await response.text();
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = { detail: text };
    }
  }

  if (!response.ok) {
    let detail = payload?.detail;
    if (Array.isArray(detail)) {
      detail = detail.map((item) => item.msg || "Invalid value").join("; ");
    }
    throw new ApiError(detail || `Request failed (${response.status}).`, response.status);
  }
  return payload;
}

export const api = {
  health: () => request("/api/health"),
  register: (data) => request("/api/auth/register", { method: "POST", body: data }),
  login: (data) => request("/api/auth/login", { method: "POST", body: data }),
  me: () => request("/api/auth/me", { auth: true }),
  predict: (text) => request("/api/predict", { method: "POST", body: { text }, auth: true }),
  history: (limit = 20, offset = 0) =>
    request(`/api/predictions?limit=${limit}&offset=${offset}`, { auth: true }),
  stats: () => request("/api/predictions/stats", { auth: true }),
  deletePrediction: (id) =>
    request(`/api/predictions/${id}`, { method: "DELETE", auth: true }),
  clearHistory: () => request("/api/predictions", { method: "DELETE", auth: true }),
  insights: () => request("/api/insights"),
};
