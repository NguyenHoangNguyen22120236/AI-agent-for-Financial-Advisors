export async function sendMessage(payload) {
  const token = localStorage.getItem("access_token");


  const resp = await fetch(`${process.env.REACT_APP_API_URL}/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  const data = await resp.json();
  return {
    reply: data.response,
    toolCalls: data.tool_calls,
    sessionId: data.session_id,
  };
}
