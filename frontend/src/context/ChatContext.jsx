import React, { createContext, useContext, useState, useEffect } from 'react';
import { postChat, scheduleCheck, createBooking, getPricing, getCalendarAuth } from '../lib/api.js';

const ChatContext = createContext();

const generateSessionId = () => {
  return crypto.randomUUID();
};

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([{ id: 1, role: "assistant", content: "Hi — I'm Metalogics Assistant. How can I help today?" }]);
  const [sessionId, setSessionId] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    const stored = localStorage.getItem('chatSessionId');
    if (stored) {
      setSessionId(stored);
    } else {
      const newId = generateSessionId();
      setSessionId(newId);
      localStorage.setItem('chatSessionId', newId);
    }
  }, []);

  const handleBookingSubmit = async (selectedDateTime) => {
    const startTime = new Date(selectedDateTime).toISOString();
    const schedulePayload = {
      user: 'user',
      start: startTime,
      duration: 60
    };
    try {
      const scheduleResult = await scheduleCheck(schedulePayload);
      if (scheduleResult.allowed) {
        const bookingPayload = {
          user: 'user',
          start: startTime,
          duration: 60,
          summary: 'Consultation Booking',
          description: 'Booked via chatbot'
        };
        const bookingResult = await createBooking(bookingPayload);
        const successMessage = { id: Date.now(), role: 'assistant', content: `Booking confirmed! ${bookingResult.reason}` };
        setMessages(prev => [...prev, successMessage]);
      } else {
        const failureMessage = { id: Date.now(), role: 'assistant', content: `Sorry, that time is not available. ${scheduleResult.reason}` };
        setMessages(prev => [...prev, failureMessage]);
      }
    } catch (error) {
      const errorMessage = { id: Date.now(), role: 'assistant', content: 'An error occurred while booking. Please try again.' };
      setMessages(prev => [...prev, errorMessage]);
      console.error('Booking error:', error);
    }
  };

  const sendMessage = async (text) => {
    const userMessage = { id: Date.now(), role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    setSuggestions([]);

    try {
      const response = await postChat(text, sessionId);
      const botMessage = { id: Date.now() + 1, role: 'assistant', content: response.answer };
      setMessages(prev => [...prev, botMessage]);
      setSuggestions(response.upsell ? response.upsell.map(u => u.text || u) : []);

      // Check for intent in the response
      const intent = response.intent_hint;
      if (intent) {
        if (intent === 'booking') {
          // Show booking picker
          const pickerMessage = { id: Date.now() + 2, role: 'assistant', type: 'booking_picker' };
          setMessages(prev => [...prev, pickerMessage]);
        } else if (intent === 'pricing') {
          const serviceMatch = response.answer.match(/service:\s*(\w+)/);
          const service = serviceMatch ? serviceMatch[1] : 'web-development';
          const pricing = await getPricing(service);
          const pricingMessage = { id: Date.now() + 2, role: 'assistant', type: 'pricing', data: pricing };
          setMessages(prev => [...prev, pricingMessage]);
        } else if (intent === 'calendar_auth') {
          const auth = await getCalendarAuth();
          const authMessage = { id: Date.now() + 2, role: 'assistant', content: `Please authorize your calendar: <a href="${auth.auth_url}" target="_blank">Authorize Calendar</a>` };
          setMessages(prev => [...prev, authMessage]);
        }
      }
    } catch (error) {
      // Remove the optimistic message on error
      setMessages(prev => prev.slice(0, -1));
      console.error('Failed to send message:', error);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <ChatContext.Provider value={{ messages, sessionId, sendMessage, handleBookingSubmit, isTyping, suggestions }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => useContext(ChatContext);