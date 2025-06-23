import React from "react";

export default function ChatMessage({ sender, text }) {
  const isUser = sender === "user";
  return (
    <div className={`chat-message ${isUser ? "user" : "ai"}`}>
      {!isUser && <div className="sender-label">🤖</div>}
      <div className="chat-bubble">{text}</div>
    </div>
  );
}
