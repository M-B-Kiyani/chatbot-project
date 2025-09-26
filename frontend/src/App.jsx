import React, { useState, useEffect, useRef } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';

function App() {
  const [messages, setMessages] = useState([
    { id: 1, role: "assistant", text: "Hi — I'm Metalogics Assistant. How can I help today?" }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showBooking, setShowBooking] = useState(false);
  const [bookingInfo, setBookingInfo] = useState({ duration: 30, time: null });
  const [suggestions, setSuggestions] = useState([]);
  const bottomRef = useRef();
  const baseApiUrl = "http://localhost:8000";

  useEffect(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), [messages, isTyping]);

  async function sendMessage(text) {
    if (!text?.trim()) return;
    const userMsg = { id: Date.now(), role: "user", text };
    setMessages(m => [...m, userMsg]);
    setInput("");
    setIsTyping(true);
    setSuggestions([]); // clear suggestions while processing

    try {
      const res = await fetch(`${baseApiUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
      const data = await res.json();
      // Expecting shape: { reply, suggestions?: [], intent?: 'webdev' }
      if (data?.reply) {
        setMessages(m => [...m, { id: Date.now()+1, role: "assistant", text: data.reply }]);
      }
      if (data?.suggestions) setSuggestions(data.suggestions);
      if (data?.intent) handleIntent(data.intent, data);
      // If backend suggests booking option
      if (data?.action === "open_booking") setShowBooking(true);
    } catch (err) {
      setMessages(m => [...m, { id: Date.now()+2, role: "assistant", text: "Sorry — something went wrong. Try again later." }]);
    } finally {
      setIsTyping(false);
    }
  }

  function handleIntent(intent, data) {
    // simple upsell rule: if user interested in web dev, recommend SEO + Design
    if (intent === "interested_webdev") {
      setMessages(m => [...m, {
        id: Date.now()+3,
        role: "assistant",
        text: "I see you're interested in web development — we also offer SEO and graphic design packages to help launch apps. Would you like pricing options?"
      }]);
      setSuggestions(["Show pricing", "Discuss SEO package", "Book a call"]);
    }
  }

  async function startGoogleAuth() {
    // open oauth flow
    window.open(`${baseApiUrl}/api/calendar/auth`, "_blank", "noopener");
  }

  async function createBooking() {
    setIsTyping(true);
    try {
      const res = await fetch(`${baseApiUrl}/api/create-booking`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ duration: bookingInfo.duration, time: bookingInfo.time })
      });
      const data = await res.json();
      if (data.success) {
        setMessages(m => [...m, { id: Date.now()+4, role: "assistant", text: `Booked! ${data.eventLink ?? ""}` }]);
        // optionally upsert lead to HubSpot:
        if (data.lead) await fetch(`${baseApiUrl}/api/upsert-hubspot`, {
          method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(data.lead)
        });
      } else {
        setMessages(m => [...m, { id: Date.now()+5, role: "assistant", text: `Unable to book: ${data.message}` }]);
      }
    } catch (err) {
      setMessages(m => [...m, { id: Date.now()+6, role: "assistant", text: "Booking failed — try again later." }]);
    } finally {
      setShowBooking(false);
      setIsTyping(false);
    }
  }

  return (
    <div className="h-screen flex flex-col bg-white">
      {/* Header hidden for embedding */}
      {/* <header className="bg-gray-100 p-4">
        <h1 className="text-xl font-bold">Metalogics AI Chat</h1>
      </header> */}

      <ChatWindow messages={messages} isTyping={isTyping} bottomRef={bottomRef} onOpenBooking={() => setShowBooking(true)} />
      <ChatInput input={input} setInput={setInput} sendMessage={sendMessage} suggestions={suggestions} setShowBooking={setShowBooking} />

      {/* Booking modal */}
      {showBooking && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-lg">
            <h3 className="font-semibold text-lg mb-4">Create Booking</h3>
            <label className="block mb-2 text-sm">Duration</label>
            <select value={bookingInfo.duration} onChange={e=>setBookingInfo({...bookingInfo,duration: parseInt(e.target.value)})} className="w-full p-2 border rounded mb-4">
              <option value={15}>15 minutes</option>
              <option value={30}>30 minutes</option>
              <option value={60}>60 minutes</option>
            </select>
            <label className="block mb-2 text-sm">Preferred time (ISO)</label>
            <input value={bookingInfo.time||""} onChange={e=>setBookingInfo({...bookingInfo,time: e.target.value})} placeholder="YYYY-MM-DDTHH:MM" className="w-full p-2 border rounded mb-4" />
            <div className="flex gap-2 justify-end">
              <button onClick={()=>setShowBooking(false)} className="px-4 py-2 rounded border hover:bg-gray-100">Cancel</button>
              <button onClick={createBooking} className="px-4 py-2 rounded bg-blue-500 text-white hover:bg-blue-600">Confirm</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
