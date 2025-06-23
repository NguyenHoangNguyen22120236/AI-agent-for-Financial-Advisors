import React, { useState, useRef } from "react";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";
import Sidebar from "../components/Sidebar";
import ChatMessage from "../components/ChatMessage";
import { useAuth } from "../context/AuthContext";
import { sendMessage } from "../api/chat";
import "../styles/ChatPage.css";

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const chatBottomRef = useRef();
  const { user } = useAuth();

  const handleSend = async (text) => {
    const userMsg = { sender: "user", text };
    setMessages((msgs) => [...msgs, userMsg]);
    setIsThinking(true);

    try {
      const {
        reply,
        sessionId: returnedSessionId,
        toolCalls,
      } = await sendMessage({
        message: text,
        user_id: user.id,
        session_id: sessionId,
      });

      const aiMsg = { sender: "ai", text: reply };
      setMessages((msgs) => [...msgs, aiMsg]); // ✅ Only add AI message now

      setSessionId(returnedSessionId || sessionId);
    } catch (err) {
      setMessages((msgs) => [
        ...msgs,
        { sender: "ai", text: "❌ Error contacting assistant." },
      ]);
    } finally {
      setIsThinking(false);
      chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  };

  if (!user) return null;

  return (
    <div className="chat-page">
      <Sidebar />
      <div className="chat-main">
        {!user.hubspot_connected && (
          <button
            className="hubspot-btn"
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
        )}

        <ChatWindow messages={messages} />
        {isThinking && <div className="thinking">🤖 AI is thinking...</div>}
        <ChatInput onSend={handleSend} />
        <div ref={chatBottomRef} />
      </div>
    </div>
  );
}
