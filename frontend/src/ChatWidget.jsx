import React, { useState } from "react";
import {
  MessageCircle,
  Send,
  Bot,
  User,
  Loader2,
  X,
  Sun,
  Moon,
  Zap,
  Calendar,
  Phone,
} from "lucide-react";

const ChatWidget = ({ onBookDemo }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your Metalogics AI assistant. How can I help you today?",
      sender: "bot",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(true);
  const [apiBaseUrl] = useState(
    process.env.REACT_APP_API_BASE_URL || "http://localhost:8000"
  );
  const [sessionId] = useState(
    `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  );
  const [logoError, setLogoError] = useState(false);

  const toggleChat = () => setIsOpen(!isOpen);
  const toggleTheme = () => setIsDarkMode(!isDarkMode);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: messages.length + 1,
      text: inputMessage,
      sender: "user",
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = inputMessage;
    setInputMessage("");
    setIsLoading(true);
    setShowQuickActions(false);

    try {
      const chatResponse = await fetch(`${apiBaseUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: currentInput,
          session_id: sessionId,
        }),
      });

      if (!chatResponse.ok) {
        throw new Error(`Chat API failed: ${chatResponse.status}`);
      }

      const chatData = await chatResponse.json();

      const botResponse = {
        id: messages.length + 2,
        text: chatData.response,
        sender: "bot",
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, botResponse]);
    } catch (error) {
      console.error("Error:", error);
      const errorResponse = {
        id: messages.length + 2,
        text: "I'm sorry, I'm having trouble connecting right now. Please make sure the backend server is running and try again.",
        sender: "bot",
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = async (action) => {
    switch (action) {
      case "services":
        setInputMessage("What services do you offer?");
        setShowQuickActions(false);
        setTimeout(() => {
          handleSendMessage({ preventDefault: () => {} });
        }, 100);
        break;
      case "pricing":
        setInputMessage("Can you show me your pricing for web development?");
        setShowQuickActions(false);
        setTimeout(() => {
          handleSendMessage({ preventDefault: () => {} });
        }, 100);
        break;
      case "demo":
        if (onBookDemo) {
          onBookDemo();
        } else {
          setInputMessage("I'd like to book a demo call");
          setShowQuickActions(false);
          setTimeout(() => {
            handleSendMessage({ preventDefault: () => {} });
          }, 100);
        }
        break;
      case "portfolio":
        setInputMessage("Can you tell me about your previous projects?");
        setShowQuickActions(false);
        setTimeout(() => {
          handleSendMessage({ preventDefault: () => {} });
        }, 100);
        break;
      default:
        return;
    }
  };

  return (
    <>
      {/* Floating Chat Bubble */}
      <div
        className="fixed bottom-6 right-6 z-50"
        style={{
          transform: "scale(1)",
          transition: "transform 0.3s ease",
        }}
      >
        <button
          onClick={toggleChat}
          className="w-14 h-14 rounded-full shadow-lg flex items-center justify-center text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:shadow-xl transition-shadow duration-300"
          style={{
            transform: "scale(1)",
          }}
          onMouseEnter={(e) => (e.target.style.transform = "scale(1.05)")}
          onMouseLeave={(e) => (e.target.style.transform = "scale(1)")}
        >
          {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
        </button>
      </div>

      {/* Chat Window */}
      {isOpen && (
        <div
          className={`fixed bottom-24 right-6 w-96 h-[600px] rounded-2xl shadow-2xl z-40 flex flex-col overflow-hidden ${
            isDarkMode ? "bg-gray-900 text-gray-100" : "bg-white text-gray-900"
          }`}
          style={{
            opacity: 1,
            transform: "translateY(0) scale(1)",
            transition: "opacity 0.3s ease, transform 0.3s ease",
          }}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                  {!logoError ? (
                    <img
                      src="/assets/metalogics icon.png"
                      alt="Metalogics"
                      className="w-6 h-6 object-contain"
                      onError={() => setLogoError(true)}
                    />
                  ) : (
                    <Bot className="w-6 h-6" />
                  )}
                </div>
                <div>
                  <h3 className="font-semibold text-sm">Metalogics AI</h3>
                  <p className="text-xs opacity-90">Online</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={toggleTheme}
                  className="p-1 rounded-full hover:bg-white/20 transition-colors"
                >
                  {isDarkMode ? <Sun size={16} /> : <Moon size={16} />}
                </button>
                <button
                  onClick={toggleChat}
                  className="p-1 rounded-full hover:bg-white/20 transition-colors"
                >
                  <X size={16} />
                </button>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.sender === "user" ? "justify-end" : "justify-start"
                }`}
                style={{
                  opacity: 1,
                  transform: "translateY(0)",
                  transition: "opacity 0.3s ease, transform 0.3s ease",
                }}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2 shadow-md ${
                    message.sender === "user"
                      ? "bg-gradient-to-r from-indigo-500 to-purple-500 text-white"
                      : isDarkMode
                      ? "bg-gray-800 text-gray-100"
                      : "bg-gray-100 text-gray-900"
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                  <p
                    className={`text-xs mt-1 ${
                      message.sender === "user"
                        ? "text-white/70"
                        : isDarkMode
                        ? "text-gray-400"
                        : "text-gray-500"
                    }`}
                  >
                    {message.timestamp}
                  </p>
                </div>
              </div>
            ))}

            {/* Quick Actions */}
            {showQuickActions && messages.length === 1 && (
              <div className="space-y-2">
                <p
                  className={`text-sm text-center ${
                    isDarkMode ? "text-gray-300" : "text-gray-600"
                  }`}
                >
                  Quick actions:
                </p>
                <div className="grid grid-cols-1 gap-2">
                  <button
                    onClick={() => handleQuickAction("services")}
                    className="flex items-center space-x-2 p-3 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 transition-all duration-200 border border-blue-200"
                  >
                    <Zap className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-900">
                      Our Services
                    </span>
                  </button>
                  <button
                    onClick={() => handleQuickAction("pricing")}
                    className="flex items-center space-x-2 p-3 rounded-xl bg-gradient-to-r from-green-50 to-emerald-50 hover:from-green-100 hover:to-emerald-100 transition-all duration-200 border border-green-200"
                  >
                    <Calendar className="w-4 h-4 text-green-600" />
                    <span className="text-sm font-medium text-green-900">
                      View Pricing
                    </span>
                  </button>
                  <button
                    onClick={() => handleQuickAction("portfolio")}
                    className="flex items-center space-x-2 p-3 rounded-xl bg-gradient-to-r from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 transition-all duration-200 border border-purple-200"
                  >
                    <Phone className="w-4 h-4 text-purple-600" />
                    <span className="text-sm font-medium text-purple-900">
                      Our Portfolio
                    </span>
                  </button>
                  <button
                    onClick={() => handleQuickAction("demo")}
                    className="flex items-center space-x-2 p-3 rounded-xl bg-gradient-to-r from-orange-50 to-red-50 hover:from-orange-100 hover:to-red-100 transition-all duration-200 border border-orange-200"
                  >
                    <Calendar className="w-4 h-4 text-orange-600" />
                    <span className="text-sm font-medium text-orange-900">
                      Book Demo
                    </span>
                  </button>
                </div>
              </div>
            )}

            {isLoading && (
              <div className="flex justify-start">
                <div
                  className={`rounded-2xl px-4 py-2 shadow-md ${
                    isDarkMode ? "bg-gray-800" : "bg-gray-100"
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
                    <span
                      className={`text-sm ${
                        isDarkMode ? "text-gray-300" : "text-gray-600"
                      }`}
                    >
                      Thinking...
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div
            className={`p-4 border-t ${
              isDarkMode ? "border-gray-700" : "border-gray-200"
            }`}
          >
            <form onSubmit={handleSendMessage} className="flex space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message..."
                className={`flex-1 px-4 py-2 rounded-full border focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                  isDarkMode
                    ? "bg-gray-800 border-gray-600 text-gray-100 placeholder-gray-400"
                    : "bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-500"
                }`}
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors ${
                  inputMessage.trim() && !isLoading
                    ? "bg-gradient-to-r from-indigo-500 to-purple-500 text-white hover:from-indigo-600 hover:to-purple-600"
                    : isDarkMode
                    ? "bg-gray-700 text-gray-400 cursor-not-allowed"
                    : "bg-gray-300 text-gray-500 cursor-not-allowed"
                }`}
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatWidget;
