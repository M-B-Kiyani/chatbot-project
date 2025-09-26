import React from 'react';
import ChatbotWidget from './components/ChatbotWidget/ChatbotWidget';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl h-[80vh] bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="h-full flex flex-col">
          <div className="bg-gradient-to-r from-sky-600 to-indigo-600 text-white p-4">
            <h1 className="text-xl font-semibold">Metalogics Chatbot</h1>
            <p className="text-sm opacity-90">AI-powered assistant for your needs</p>
          </div>
          <div className="flex-1 overflow-hidden">
            <ChatbotWidget />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
