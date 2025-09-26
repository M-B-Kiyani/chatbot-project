import React, { useState } from 'react';
import { useChat } from '../context/ChatContext';

const BookingPicker = () => {
  const [selectedDateTime, setSelectedDateTime] = useState('');
  const [loading, setLoading] = useState(false);
  const { handleBookingSubmit } = useChat();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedDateTime) return;

    setLoading(true);
    try {
      await handleBookingSubmit(selectedDateTime);
    } catch (error) {
      console.error('Booking submit error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h3 className="text-lg font-semibold text-blue-800 mb-3">Schedule a Consultation</h3>
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label htmlFor="datetime" className="block text-sm font-medium text-blue-700 mb-1">
            Select Date and Time:
          </label>
          <input
            type="datetime-local"
            id="datetime"
            value={selectedDateTime}
            onChange={(e) => setSelectedDateTime(e.target.value)}
            className="w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading || !selectedDateTime}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Checking availability...' : 'Book Consultation'}
        </button>
      </form>
    </div>
  );
};

export default BookingPicker;