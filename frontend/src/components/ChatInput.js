import React, { useState } from "react";

export default function ChatInput({ onSend }) {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim()) {
      onSend(text);
      setText("");
    }
  };

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      <input
        className="chat-input"
        type="text"
        value={text}
        placeholder="Ask anything or give a task..."
        onChange={(e) => setText(e.target.value)}
      />
      <button type="submit" className="send-button">➤</button>
    </form>
  );
}
