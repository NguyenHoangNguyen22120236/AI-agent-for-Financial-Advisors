import React from "react";
import "../styles/Login.css"; // You can use the CSS below

function Login() {
  const handleGoogleLogin = async () => {
    const resp = await fetch(`${process.env.REACT_APP_API_URL}/auth/google/login`);
    const data = await resp.json();
    window.location.href = data.auth_url; // Redirects to Google
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>
          Welcome to <span className="highlight">Financial Advisor AI</span>
        </h2>
        <p className="subtitle">
          Sign in to access your smart assistant and automate your workflow.
        </p>
        <button className="oauth-btn" onClick={handleGoogleLogin}>
          <span className="google-icon" role="img" aria-label="Google">🔒</span>
          Sign in with Google
        </button>
      </div>
    </div>
  );
}


export default Login;
