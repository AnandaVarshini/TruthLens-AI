import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import Dashboard from "./pages/Dashboard";
import Detect from "./pages/Detect";
import History from "./pages/History";
import Home from "./pages/Home";
import Insights from "./pages/Insights";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import Register from "./pages/Register";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="insights" element={<Insights />} />
        <Route
          path="dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="detect"
          element={
            <ProtectedRoute>
              <Detect />
            </ProtectedRoute>
          }
        />
        <Route
          path="history"
          element={
            <ProtectedRoute>
              <History />
            </ProtectedRoute>
          }
        />
        <Route
          path="profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="*"
          element={
            <div className="container section text-center">
              <h2>Page not found</h2>
              <p>The page you requested does not exist.</p>
              <a href="/" className="btn btn-primary">
                Back to home
              </a>
            </div>
          }
        />
      </Route>
    </Routes>
  );
}
