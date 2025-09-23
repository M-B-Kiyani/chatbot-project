// Chatbot Widget Script

document.addEventListener("DOMContentLoaded", function () {
  const chatToggle = document.getElementById("chat-toggle");
  const chatWindow = document.getElementById("chat-window");
  const chatClose = document.getElementById("chat-close");
  const messageInput = document.getElementById("message-input");
  const sendButton = document.getElementById("send-button");
  const messages = document.getElementById("messages");
  const quickActions = document.querySelectorAll(".quick-action");

  // Toggle chat window
  function toggleChat() {
    const isHidden = chatWindow.classList.contains("hidden");
    chatWindow.classList.toggle("hidden");
    chatWindow.classList.toggle("open");
    if (isHidden) {
      // Opening: add flex layout
      chatWindow.classList.add("flex", "flex-col");
    } else {
      // Closing: remove flex layout
      chatWindow.classList.remove("flex", "flex-col");
    }
    if (!chatWindow.classList.contains("hidden")) {
      messageInput.focus();
    }
  }

  chatToggle.addEventListener("click", toggleChat);
  chatClose.addEventListener("click", toggleChat);

  // Send message
  function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
      addMessage(message, "user");
      messageInput.value = "";
      // Simulate bot response (replace with API call)
      setTimeout(() => {
        addMessage(
          "Thank you for your message. Our team will get back to you soon!",
          "bot"
        );
      }, 1000);
    }
  }

  sendButton.addEventListener("click", sendMessage);
  messageInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

  // Add message to chat
  function addMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `flex ${
      sender === "user" ? "justify-end" : "justify-start"
    }`;

    const bubble = document.createElement("div");
    bubble.className = `${sender}-message rounded-lg px-4 py-2 max-w-xs break-words`;
    bubble.textContent = text;

    messageDiv.appendChild(bubble);
    messages.appendChild(messageDiv);

    // Scroll to bottom
    messages.scrollTop = messages.scrollHeight;
  }

  // Quick actions
  quickActions.forEach((button) => {
    button.addEventListener("click", function () {
      const message = this.getAttribute("data-message");
      addMessage(message, "user");
      // Simulate response
      setTimeout(() => {
        addMessage(`You selected: ${message}. How can we help further?`, "bot");
      }, 1000);
    });
  });

  // Placeholder for API integration
  function sendToAPI(message) {
    // Implement API call here
    // fetch('/api/chat', { method: 'POST', body: JSON.stringify({ message }) })
    // .then(response => response.json())
    // .then(data => addMessage(data.response, 'bot'));
    console.log("Sending to API:", message);
  }

  // Update sendMessage to use API
  // In sendMessage, after addMessage(message, 'user'), call sendToAPI(message);
  // And in the response, addMessage(response, 'bot');
});
