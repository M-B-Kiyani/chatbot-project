import React from 'react';
import PricingCard from './PricingCard';
import BookingConfirmation from './BookingConfirmation';
import BookingPicker from './BookingPicker';
import LinkButton from './LinkButton';
import { useChat } from '../context/ChatContext';

export default function ChatWindow({ messages, isTyping, bottomRef, onOpenBooking }) {
  const { sendMessage } = useChat();
  const renderMessageContent = (message) => {
    switch (message.type) {
      case 'pricing':
        return <PricingCard pricingData={message.data} onSelect={sendMessage} />;
      case 'booking':
        return <BookingConfirmation bookingData={message.data} onOpenBooking={onOpenBooking} />;
      case 'booking_picker':
        return <BookingPicker />;
      case 'link':
        return <LinkButton linkData={message.data} />;
      default:
        const content = message.content || message.text || '';
        return (
          <div className="text-sm whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: content }} />
        );
    }
  };

  return (
    <div className="flex-1 p-4 overflow-y-auto space-y-3">
      {messages.map(m => (
        <div key={m.id} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
          <div className={`py-3 px-4 rounded-lg max-w-[80%] ${m.role === "user" ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-900"}`}>
            {renderMessageContent(m)}
          </div>
        </div>
      ))}
      {isTyping && <div className="text-sm text-gray-500">Assistant is typing...</div>}
      <div ref={bottomRef} />
    </div>
  );
}