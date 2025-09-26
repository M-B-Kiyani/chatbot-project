import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { api } from './api';

const ChatContext = createContext();

export const useChat = () => useContext(ChatContext);

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([
    { id: 1, role: 'assistant', text: 'Hi — I\'m Metalogics Assistant. How can I help today?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showBooking, setShowBooking] = useState(false);
  const [bookingInfo, setBookingInfo] = useState({ duration: 30, time: null });
  const [suggestions, setSuggestions] = useState([]);
  const [pricing, setPricing] = useState(null);
  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const sendMessage = async (text) => {
    if (!text?.trim()) return;
    const userMsg = { id: Date.now(), role: 'user', text };
    setMessages(m => [...m, userMsg]);
    setInput('');
    setIsTyping(true);
    setSuggestions([]);

    try {
      const data = await api.chat(text);
      if (data?.answer) {
        setMessages(m => [...m, { id: Date.now() + 1, role: 'assistant', text: data.answer }]);
      }
      if (data?.intent_hint) handleIntent(data.intent_hint, data);
      // For now, assume booking is triggered by intent or user action
    } catch (err) {
      setMessages(m => [...m, { id: Date.now() + 2, role: 'assistant', text: 'Sorry — something went wrong. Try again later.' }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleIntent = async (intent, data) => {
    if (intent === 'booking') {
      // Check schedule before booking
      try {
        const scheduleData = await api.scheduleCheck({ time: bookingInfo.time });
        if (scheduleData.available) {
          setShowBooking(true);
        } else {
          setMessages(m => [...m, { id: Date.now() + 3, role: 'assistant', text: 'Sorry, that time is not available. Please choose another time.' }]);
        }
      } catch (err) {
        setMessages(m => [...m, { id: Date.now() + 4, role: 'assistant', text: 'Unable to check schedule. Please try again.' }]);
      }
    } else if (intent === 'pricing') {
      try {
        const pricingData = await api.getPricing('web-development');
        setPricing(pricingData);
        setMessages(m => [...m, { id: Date.now() + 5, role: 'assistant', text: `Here are our pricing options for web development: ${pricingData.description || 'Please check the details below.'}` }]);
      } catch (err) {
        setMessages(m => [...m, { id: Date.now() + 6, role: 'assistant', text: 'Unable to fetch pricing. Please try again.' }]);
      }
    } else if (intent === 'auth_required') {
      setMessages(m => [...m, { id: Date.now() + 7, role: 'assistant', text: 'To proceed, please authenticate with your calendar or HubSpot account.' }]);
    }
  };

  const createBooking = async () => {
    setIsTyping(true);
    try {
      const data = await api.createBooking({ duration: bookingInfo.duration, time: bookingInfo.time });
      if (data.allowed) {
        setMessages(m => [...m, { id: Date.now() + 8, role: 'assistant', text: `Booked! Event ID: ${data.event_id}` }]);
      } else {
        setMessages(m => [...m, { id: Date.now() + 9, role: 'assistant', text: `Unable to book: ${data.reason}` }]);
      }
    } catch (err) {
      setMessages(m => [...m, { id: Date.now() + 10, role: 'assistant', text: 'Booking failed — try again later.' }]);
    } finally {
      setShowBooking(false);
      setIsTyping(false);
    }
  };

  const startCalendarAuth = () => {
    api.calendarAuth();
  };

  const startHubspotAuth = () => {
    api.hubspotAuth();
  };

  return (
    <ChatContext.Provider value={{
      messages,
      input,
      setInput,
      isTyping,
      showBooking,
      setShowBooking,
      bookingInfo,
      setBookingInfo,
      suggestions,
      pricing,
      bottomRef,
      sendMessage,
      createBooking,
      startCalendarAuth,
      startHubspotAuth
    }}>
      {children}
    </ChatContext.Provider>
  );
};