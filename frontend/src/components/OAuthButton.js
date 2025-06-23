import React from "react";

function OAuthButton({ provider, onClick }) {
  return (
    <button className="oauth-btn" onClick={onClick}>
      Sign in with {provider}
    </button>
  );
}

export default OAuthButton;
