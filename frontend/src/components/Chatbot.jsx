import React, { useState, useRef, useEffect } from 'react';
import { ChatProvider, useChat } from '../context/ChatContext';
import ChatWindow from './ChatWindow';
import ChatInput from './ChatInput';

function ChatbotInner() {
  const { messages, sendMessage, isTyping, suggestions, handleBookingSubmit } = useChat();
  const [input, setInput] = useState('');
  const [showBooking, setShowBooking] = useState(false);
  const [bookingInfo, setBookingInfo] = useState({ duration: 30, time: null });
  const bottomRef = useRef();

  useEffect(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), [messages, isTyping]);

  const handleSendMessage = (text) => {
    if (!text?.trim()) return;
    setInput('');
    sendMessage(text);
  };

  const createBooking = async () => {
    if (bookingInfo.time) {
      await handleBookingSubmit(bookingInfo.time);
      setShowBooking(false);
    }
  };

  return (
    <div className="fixed right-6 bottom-6 w-80 max-w-full md:w-96 z-50">
      <div className="bg-white shadow-2xl rounded-2xl overflow-hidden border">
        <div className="px-4 py-3 bg-gradient-to-r from-sky-600 to-indigo-600 text-white flex items-center justify-between">
          <div>
            <div className="font-semibold text-sm">Metalogics Assistant</div>
            <div className="text-xs opacity-90">AI · Calendar · HubSpot</div>
          </div>
        </div>

        <ChatWindow messages={messages} isTyping={isTyping} bottomRef={bottomRef} onOpenBooking={() => setShowBooking(true)} />
        <ChatInput input={input} setInput={setInput} sendMessage={handleSendMessage} suggestions={suggestions} setShowBooking={setShowBooking} />
      </div>

      {/* Booking modal */}
      {showBooking && (
        <div className="fixed inset-0 z-60 flex items-end md:items-center justify-center p-4">
          <div className="bg-white rounded-xl p-4 w-full max-w-md shadow-lg">
            <h3 className="font-semibold">Create Booking</h3>
            <label className="block mt-2 text-xs">Duration</label>
            <select value={bookingInfo.duration} onChange={e=>setBookingInfo({...bookingInfo,duration: parseInt(e.target.value)})} className="w-full p-2 border rounded mt-1">
              <option value={15}>15 minutes</option>
              <option value={30}>30 minutes</option>
              <option value={60}>60 minutes</option>
            </select>
            <label className="block mt-2 text-xs">Preferred time (ISO)</label>
            <input value={bookingInfo.time||""} onChange={e=>setBookingInfo({...bookingInfo,time: e.target.value})} placeholder="YYYY-MM-DDTHH:MM" className="w-full p-2 border rounded mt-1" />
            <div className="flex gap-2 justify-end mt-4">
              <button onClick={()=>setShowBooking(false)} className="px-3 py-1 rounded border">Cancel</button>
              <button onClick={createBooking} className="px-3 py-1 rounded bg-sky-600 text-white">Confirm</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function Chatbot() {
  return (
    <ChatProvider>
      <ChatbotInner />
    </ChatProvider>
  );
}