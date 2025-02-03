document.addEventListener("DOMContentLoaded", () => {
  const chatPlaceholder = document.getElementById("chat-placeholder");
  const chatBox = document.getElementById("chat-box");
  const chatHeader = document.getElementById("chat-header");
  const chatMessages = document.getElementById("chat-messages");
  const messageInput = document.getElementById("message-input");
  const sendButton = document.getElementById("send-button");
  const friendsList = document.getElementById("friends-list");
  const groupsList = document.getElementById("groups-list");

  // Verificar si hay un token
  const token = localStorage.getItem("token");
  if (!token) {
    // Si no hay token, redirigir al login
    window.location.href = "index.html";
    return;
  }

  // Configurar encabezados para solicitudes protegidas
  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };

  // Logout
  const logoutButton = document.getElementById("logout-button"); // Asegúrate de agregar este botón en el HTML
  if (logoutButton) {
    logoutButton.addEventListener("click", () => {
      localStorage.removeItem("token");
      window.location.href = "index.html";
    });
  }

  // Fetch friends and groups from the server
  async function fetchFriendsAndGroups() {
    try {
      const [friendsResponse, groupsResponse] = await Promise.all([
        fetch("http://127.0.0.1:8000/friends", { headers }),
        fetch("http://127.0.0.1:8000/groups", { headers }),
      ]);

      if (!friendsResponse.ok || !groupsResponse.ok) {
        throw new Error("Error fetching data");
      }

      const friends = await friendsResponse.json();
      const groups = await groupsResponse.json();

      renderList(friendsList, friends);
      renderList(groupsList, groups);
    } catch (error) {
      console.error("Error fetching friends or groups:", error);
      alert("Error loading friends or groups. Please try again later.");
    }
  }

  // Render friends and groups
  function renderList(list, data) {
    list.innerHTML = ""; // Clear the list before rendering
    data.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = `${item.name} - ${item.lastMessage} (${item.time})`;
      li.addEventListener("click", () => openChat(item.name));
      list.appendChild(li);
    });
  }

  // Open chat
  function openChat(name) {
    chatHeader.textContent = name;
    chatMessages.innerHTML = ""; // Clear previous messages
    chatPlaceholder.classList.add("hidden");
    chatBox.classList.remove("hidden");

    // Load chat messages
    fetchMessages(name);
  }

  // Exit chat (return to the placeholder)
  function exitChat() {
    chatPlaceholder.classList.remove("hidden");
    chatBox.classList.add("hidden");
    chatHeader.textContent = "";
    chatMessages.innerHTML = ""; // Clear chat messages
  }

  // Fetch messages for a chat
  async function fetchMessages(chatName) {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/messages/${chatName}`,
        { headers }
      );

      if (!response.ok) {
        throw new Error("Error fetching messages");
      }

      const messages = await response.json();

      // Render messages
      messages.forEach((msg) => {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", msg.sent ? "sent" : "received");
        messageDiv.innerHTML = `<p>${msg.content}</p>`;
        chatMessages.appendChild(messageDiv);
      });

      // Scroll to the bottom
      chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  }

  // Send a message
  async function sendMessage() {
    const message = messageInput.value.trim();
    if (message === "") return;

    try {
      const response = await fetch("http://127.0.0.1:8000/send-message", {
        method: "POST",
        headers,
        body: JSON.stringify({
          content: message,
          recipient: chatHeader.textContent, // Assuming recipient is in chatHeader
        }),
      });

      if (!response.ok) {
        throw new Error("Error sending message");
      }

      const sentMessage = document.createElement("div");
      sentMessage.classList.add("message", "sent");
      sentMessage.innerHTML = `<p>${message}</p>`;
      chatMessages.appendChild(sentMessage);

      // Clear input
      messageInput.value = "";

      // Scroll to bottom of chat
      chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (error) {
      console.error("Error sending message:", error);
      alert("Failed to send message. Please try again.");
    }
  }

  // Add event listener to send button
  sendButton.addEventListener("click", sendMessage);

  // Add event listener for Enter key
  messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });

  // Add event listener for Esc key to exit chat
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      exitChat();
    }
  });

  // Fetch friends and groups when the page loads
  fetchFriendsAndGroups();
});
