import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "../styles/Sidebar.css";

export default function Sidebar() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>💼 FA.AI</h2>
      </div>

      <nav className="sidebar-nav">
        <Link to="/" className={isActive("/") ? "active" : ""}>
          💬 Chat
        </Link>
      </nav>

      {!user?.hubspot_connected && (
        <div className="connect-hubspot-warning">
          <p>⚠️ HubSpot not connected</p>
          <button
            className="connect-button"
            onClick={async () => {
              try {
                const resp = await fetch(
                  `${process.env.REACT_APP_API_URL}/auth/hubspot/login`
                );
                const data = await resp.json();
                if (data.auth_url) {
                  window.location.href = data.auth_url;
                } else {
                  console.error("Missing auth_url from response.");
                }
              } catch (err) {
                console.error("Failed to fetch HubSpot auth URL:", err);
              }
            }}
          >
            Connect HubSpot
          </button>
        </div>
      )}

      <button className="logout-button" onClick={logout}>
        🚪 Logout
      </button>
    </aside>
  );
}
