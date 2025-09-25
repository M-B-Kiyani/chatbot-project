// chatbot-widget/src/ChatbotWidget.jsx
import React, { useState, useEffect, useRef } from "react";

/*
  A minimal, responsive chatbot assistant component:
  - uses Tailwind for styling
  - talks to backend endpoints described in README
  - supports quick suggestions, booking modal, google auth button
*/

export default function ChatbotWidget({ baseApiUrl = "" }) {
  const [messages, setMessages] = useState([
    { id: 1, role: "assistant", text: "Hi — I’m Metalogics Assistant. How can I help today?" }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showBooking, setShowBooking] = useState(false);
  const [bookingInfo, setBookingInfo] = useState({ duration: 30, time: null });
  const [suggestions, setSuggestions] = useState([]);
  const bottomRef = useRef();

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
    <div className="fixed right-6 bottom-6 w-80 max-w-full md:w-96 z-50">
      <div className="bg-white shadow-2xl rounded-2xl overflow-hidden border">
        <div className="px-4 py-3 bg-gradient-to-r from-sky-600 to-indigo-600 text-white flex items-center justify-between">
          <div>
            <div className="font-semibold text-sm">Metalogics Assistant</div>
            <div className="text-xs opacity-90">AI · Calendar · HubSpot</div>
          </div>
          <button onClick={startGoogleAuth} className="text-xs bg-white/20 px-2 py-1 rounded">Connect Calendar</button>
        </div>

        <div className="p-3 max-h-72 overflow-y-auto space-y-2">
          {messages.map(m => (
            <div key={m.id} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
              <div className={`py-2 px-3 rounded-lg max-w-[80%] ${m.role === "user" ? "bg-slate-100 text-slate-800" : "bg-sky-50 text-slate-900"}`}>
                <div className="text-sm whitespace-pre-wrap">{m.text}</div>
              </div>
            </div>
          ))}
          {isTyping && <div className="text-xs text-slate-500">Assistant is typing...</div>}
          <div ref={bottomRef} />
        </div>

        {/* quick suggestions */}
        {suggestions?.length > 0 && (
          <div className="px-3 py-2 border-t flex flex-wrap gap-2 bg-gray-50">
            {suggestions.map((s,i)=>(
              <button key={i} onClick={() => sendMessage(s)} className="text-xs px-3 py-1 rounded-full bg-white shadow-sm">{s}</button>
            ))}
          </div>
        )}

        <div className="px-3 py-2 border-t bg-white flex items-center gap-2">
          <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e => { if (e.key === "Enter") sendMessage(input) }} placeholder="Type a message..." className="flex-1 text-sm p-2 rounded-md border" />
          <button onClick={() => sendMessage(input)} className="bg-sky-600 text-white px-3 py-2 rounded-md text-sm">Send</button>
          <button onClick={() => setShowBooking(true)} title="Book" className="ml-1 text-slate-600 text-sm">📅</button>
        </div>
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
