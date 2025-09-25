/**
 * Chatbot Frontend Main Entry Point
 */
<ChatbotWidget baseApiUrl={import.meta.env.VITE_API_BASE || ""} />
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

console.log('🚀 Chatbot Frontend - Project scaffold initialized!');
console.log('📁 Frontend structure ready for development');
console.log('💬 Chat UI components available');

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

