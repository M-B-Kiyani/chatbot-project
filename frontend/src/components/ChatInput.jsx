import React from 'react';

export default function ChatInput({ input, setInput, sendMessage, suggestions, setShowBooking }) {
  return (
    <>
      {/* quick suggestions */}
      {suggestions?.length > 0 && (
        <div className="px-4 py-2 border-t flex flex-wrap gap-2 bg-gray-50">
          {suggestions.map((s, i) => (
            <button key={i} onClick={() => sendMessage(s)} className="text-xs px-3 py-1 rounded-full bg-white shadow-sm border">
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="px-4 py-3 border-t bg-white flex items-center gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === "Enter") sendMessage(input) }}
          placeholder="Type a message..."
          className="flex-1 text-sm p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button onClick={() => sendMessage(input)} className="bg-blue-500 text-white px-4 py-3 rounded-lg text-sm hover:bg-blue-600">
          Send
        </button>
        <button onClick={() => setShowBooking(true)} title="Book" className="text-gray-600 text-lg hover:text-gray-800">
          📅
        </button>
      </div>
    </>
  );
}