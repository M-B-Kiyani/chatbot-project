import React from 'react';
import { useChat } from './ChatContext';

const ChatWindow = () => {
  const { messages, isTyping, suggestions, pricing, showBooking, setShowBooking, bookingInfo, setBookingInfo, createBooking, startCalendarAuth, startHubspotAuth, bottomRef } = useChat();

  return (
    <div className="flex-1 p-3 overflow-y-auto space-y-2">
      {messages.map(m => (
        <div key={m.id} className={m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
          <div className={`py-2 px-3 rounded-lg max-w-[80%] ${m.role === 'user' ? 'bg-slate-100 text-slate-800' : 'bg-sky-50 text-slate-900'}`}>
            <div className="text-sm whitespace-pre-wrap">{m.text}</div>
          </div>
        </div>
      ))}

      {pricing && (
        <div className="flex justify-start">
          <div className="py-2 px-3 rounded-lg max-w-[80%] bg-green-50 text-slate-900">
            <div className="text-sm">
              <strong>Pricing Options:</strong><br />
              {pricing.options ? pricing.options.map((opt, i) => (
                <div key={i}>{opt.name}: {opt.price}</div>
              )) : 'Details available upon request.'}
            </div>
          </div>
        </div>
      )}

      {isTyping && <div className="text-xs text-slate-500">Assistant is typing...</div>}

      <div ref={bottomRef} />

      {/* Auth Links */}
      {messages.some(m => m.text.includes('authenticate')) && (
        <div className="flex justify-start">
          <div className="py-2 px-3 rounded-lg max-w-[80%] bg-yellow-50 text-slate-900">
            <div className="text-sm">
              <button onClick={startCalendarAuth} className="bg-blue-500 text-white px-2 py-1 rounded mr-2">Connect Calendar</button>
              <button onClick={startHubspotAuth} className="bg-orange-500 text-white px-2 py-1 rounded">Connect HubSpot</button>
            </div>
          </div>
        </div>
      )}

      {/* Booking Modal */}
      {showBooking && (
        <div className="fixed inset-0 z-60 flex items-end md:items-center justify-center p-4">
          <div className="bg-white rounded-xl p-4 w-full max-w-md shadow-lg">
            <h3 className="font-semibold">Create Booking</h3>
            <label className="block mt-2 text-xs">Duration</label>
            <select
              value={bookingInfo.duration}
              onChange={e => setBookingInfo({ ...bookingInfo, duration: parseInt(e.target.value) })}
              className="w-full p-2 border rounded mt-1"
            >
              <option value={15}>15 minutes</option>
              <option value={30}>30 minutes</option>
              <option value={60}>60 minutes</option>
            </select>
            <label className="block mt-2 text-xs">Preferred time (ISO)</label>
            <input
              value={bookingInfo.time || ''}
              onChange={e => setBookingInfo({ ...bookingInfo, time: e.target.value })}
              placeholder="YYYY-MM-DDTHH:MM"
              className="w-full p-2 border rounded mt-1"
            />
            <div className="flex gap-2 justify-end mt-4">
              <button onClick={() => setShowBooking(false)} className="px-3 py-1 rounded border">Cancel</button>
              <button onClick={createBooking} className="px-3 py-1 rounded bg-sky-600 text-white">Confirm</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;