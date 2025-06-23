import React, { useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";

export default function ChatWindow({ messages }) {
  const endRef = useRef();

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chat-window">
      {messages.map((msg, i) => (
        <ChatMessage key={i} sender={msg.sender} text={msg.text} />
      ))}
      <div ref={endRef} />
    </div>
  );
}
