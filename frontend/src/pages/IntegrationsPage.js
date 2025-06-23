import React from "react";
import { hubspotLogin } from "../api/auth";

export default function IntegrationsPage() {
  return (
    <div className="integrations-page">
      <h2>Connect Your Accounts</h2>
      <button onClick={hubspotLogin}>Connect HubSpot</button>
      <p>Gmail and Calendar are connected via Google sign-in.</p>
    </div>
  );
}
