import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";

const AuthContext = createContext(null);
const TOKEN_KEY = "truthlens_token";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
  }, []);

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .me()
      .then((profile) => setUser(profile))
      .catch(() => localStorage.removeItem(TOKEN_KEY))
      .finally(() => setLoading(false));
  }, []);

  const applySession = useCallback((session) => {
    localStorage.setItem(TOKEN_KEY, session.access_token);
    setUser(session.user);
  }, []);

  const login = useCallback(
    async (email, password) => {
      const session = await api.login({ email, password });
      applySession(session);
      return session.user;
    },
    [applySession]
  );

  const register = useCallback(
    async (data) => {
      const session = await api.register(data);
      applySession(session);
      return session.user;
    },
    [applySession]
  );

  const value = useMemo(
    () => ({ user, loading, login, register, logout, isAuthenticated: Boolean(user) }),
    [user, loading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside <AuthProvider>");
  return context;
}
