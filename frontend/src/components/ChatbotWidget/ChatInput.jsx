import React from 'react';
import { useChat } from './ChatContext';

const ChatInput = () => {
  const { input, setInput, sendMessage, suggestions, setShowBooking } = useChat();

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <>
      {/* Quick suggestions */}
      {suggestions?.length > 0 && (
        <div className="px-3 py-2 border-t flex flex-wrap gap-2 bg-gray-50">
          {suggestions.map((s, i) => (
            <button
              key={i}
              onClick={() => sendMessage(s)}
              className="text-xs px-3 py-1 rounded-full bg-white shadow-sm"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="px-3 py-2 border-t bg-white flex items-center gap-2">
        <form onSubmit={handleSubmit} className="flex items-center gap-2 flex-1">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleSubmit(e); }}
            placeholder="Type a message..."
            className="flex-1 text-sm p-2 rounded-md border"
          />
          <button
            type="submit"
            className="bg-sky-600 text-white px-3 py-2 rounded-md text-sm"
          >
            Send
          </button>
        </form>
        <button
          onClick={() => setShowBooking(true)}
          title="Book"
          className="ml-1 text-slate-600 text-sm"
        >
          📅
        </button>
      </div>
    </>
  );
};

export default ChatInput;