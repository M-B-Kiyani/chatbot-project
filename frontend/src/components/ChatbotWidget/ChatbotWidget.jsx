// frontend/src/components/ChatbotWidget/ChatbotWidget.jsx
import React from 'react';
import { ChatProvider } from './ChatContext';
import ChatWindow from './ChatWindow';
import ChatInput from './ChatInput';

/*
  A minimal, responsive chatbot assistant component:
  - uses Tailwind for styling
  - talks to backend endpoints described in README
  - supports quick suggestions, booking modal, google auth button
*/

export default function ChatbotWidget() {
  return (
    <ChatProvider>
      <div className="h-full flex flex-col bg-white">
        <div className="px-4 py-3 bg-gradient-to-r from-sky-600 to-indigo-600 text-white flex items-center justify-between">
          <div>
            <div className="font-semibold text-sm">Metalogics Assistant</div>
            <div className="text-xs opacity-90">AI · Calendar · HubSpot</div>
          </div>
        </div>

        <div className="flex-1 flex flex-col overflow-hidden">
          <ChatWindow />
          <ChatInput />
        </div>
      </div>
    </ChatProvider>
  );
}