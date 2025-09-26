import React from 'react';

const BookingConfirmation = ({ bookingData, onOpenBooking }) => {
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
      <div className="flex items-center mb-3">
        <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center mr-3">
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-green-800">Booking Confirmed!</h3>
      </div>

      {bookingData && (
        <div className="text-sm text-green-700 mb-3">
          <p><strong>Date:</strong> {bookingData.date}</p>
          <p><strong>Time:</strong> {bookingData.time}</p>
          <p><strong>Service:</strong> {bookingData.service}</p>
        </div>
      )}

      <p className="text-sm text-green-700 mb-4">
        We've sent a calendar invite to your email. You'll receive a confirmation shortly.
      </p>

      <button
        onClick={onOpenBooking}
        className="w-full bg-green-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-green-700 transition-colors"
      >
        View Booking Details
      </button>
    </div>
  );
};

export default BookingConfirmation;