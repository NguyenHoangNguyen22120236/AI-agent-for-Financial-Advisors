import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import ChatPage from "./pages/ChatPage";
import IntegrationsPage from "./pages/IntegrationsPage";
import Login from "./components/Login";
import AuthCallback from "./pages/AuthCallback";

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  const token = localStorage.getItem("access_token");

  // Wait for AuthProvider to finish loading user
  if (loading) return null;

  // If token exists but user isn't set yet, you might want to still allow loading UI
  return user && token ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/login" element={<Login />} />
          <Route path="/integrations" element={
            <PrivateRoute>
              <IntegrationsPage />
            </PrivateRoute>
          }/>
          <Route path="/" element={
            <PrivateRoute>
              <ChatPage />
            </PrivateRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
