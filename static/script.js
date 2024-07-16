// Load date-fns library
const script = document.createElement("script");
script.src = "https://cdn.jsdelivr.net/npm/date-fns@2.23.0/dist/date-fns.min.js";
document.head.appendChild(script);

document.addEventListener("DOMContentLoaded", function () {
  const ws = new WebSocket("ws://localhost:5001");

  const formChat = document.getElementById("formChat");
  const username = document.getElementById("username");
  const message = document.getElementById("message");
  const subscribe = document.getElementById("subscribe");

  formChat.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = JSON.stringify({
      username: username.value,
      message: message.value,
      date: new Date().toISOString(),
    });
    ws.send(data);
    message.value = "";
  });

  ws.onopen = (e) => {
    console.log("WebSocket connection opened");
  };

  ws.onmessage = (e) => {
    console.log(e.data);
    const data = JSON.parse(e.data);

    const elMsg = document.createElement("div");
    const formattedDate = formatRelativeTime(data.date);
    elMsg.innerHTML = `<strong>${data.username}</strong> <small>(${formattedDate})</small>: ${data.message}`;
    subscribe.insertBefore(elMsg, subscribe.firstChild);
  };

  ws.onclose = (e) => {
    console.log("WebSocket connection closed");
  };

  ws.onerror = (e) => {
    console.error("WebSocket error:", e);
  };

  function formatRelativeTime(date) {
    const now = new Date();
    const messageDate = new Date(date);
    const diffInSeconds = Math.floor((now - messageDate) / 1000);

    if (diffInSeconds < 60) {
      return "just now";
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes} minute${minutes > 1 ? "s" : ""} ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours} hour${hours > 1 ? "s" : ""} ago`;
    } else {
      return dateFns.format(messageDate, "PPpp");
    }
  }
});
