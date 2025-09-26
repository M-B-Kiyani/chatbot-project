import React, { useState, useEffect } from "react";
import {
  X,
  Calendar,
  Clock,
  User,
  Mail,
  MessageSquare,
  Loader2,
  CheckCircle,
} from "lucide-react";

const BookingModal = ({ isOpen, onClose }) => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    interest: "General Consultation",
    preferredDate: "",
    preferredTime: "",
    message: "",
  });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const timeSlots = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"];

  const interests = [
    "General Consultation",
    "Web Development",
    "Mobile App Development",
    "Web3 & Blockchain",
    "SEO Optimization",
    "Graphic Design",
  ];

  useEffect(() => {
    if (!isOpen) {
      setStep(1);
      setSubmitted(false);
      setFormData({
        name: "",
        email: "",
        company: "",
        interest: "General Consultation",
        preferredDate: "",
        preferredTime: "",
        message: "",
      });
    }
  }, [isOpen]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // First, create calendar event
      const eventData = {
        summary: `Demo Call: ${formData.name} - ${formData.interest}`,
        start: `${formData.preferredDate}T${formData.preferredTime}:00`,
        end: `${formData.preferredDate}T${
          parseInt(formData.preferredTime.split(":")[0]) + 1
        }:00:00`,
        timezone: "Europe/London",
        description: `Demo call with ${formData.name} from ${
          formData.company || "N/A"
        }\nInterest: ${formData.interest}\nMessage: ${formData.message}`,
        attendees: [formData.email],
        calendar_id: "primary",
      };

      const calendarResponse = await fetch(
        "http://localhost:8000/api/calendar/create",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(eventData),
        }
      );

      if (calendarResponse.ok) {
        // Then, upsert to HubSpot
        await fetch("http://localhost:8000/api/upsert-hubspot", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: formData.name,
            email: formData.email,
            company: formData.company,
            interest: formData.interest,
            session_id: `booking_${Date.now()}`,
          }),
        });

        setSubmitted(true);
        setStep(3);
      } else {
        throw new Error("Failed to create calendar event");
      }
    } catch (error) {
      console.error("Booking error:", error);
      alert(
        "There was an error booking your demo. Please try again or contact us directly."
      );
    } finally {
      setLoading(false);
    }
  };

  const nextStep = () => {
    if (step < 3) setStep(step + 1);
  };

  const prevStep = () => {
    if (step > 1) setStep(step - 1);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">Book a Demo</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
          <div className="flex items-center space-x-4 mt-4">
            {[1, 2, 3].map((num) => (
              <div key={num} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    step >= num
                      ? "bg-metalogics-primary text-white"
                      : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {num}
                </div>
                <span
                  className={`ml-2 text-sm ${
                    step >= num ? "text-metalogics-primary" : "text-gray-600"
                  }`}
                >
                  {num === 1 ? "Details" : num === 2 ? "Schedule" : "Confirm"}
                </span>
                {num < 3 && (
                  <div
                    className={`w-12 h-0.5 ml-4 ${
                      step > num ? "bg-metalogics-primary" : "bg-gray-200"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="p-6">
          {step === 1 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Tell us about yourself
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-metalogics-primary"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-metalogics-primary"
                    required
                  />
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Company
                  </label>
                  <input
                    type="text"
                    name="company"
                    value={formData.company}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-metalogics-primary"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Interest
                  </label>
                  <select
                    name="interest"
                    value={formData.interest}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-metalogics-primary"
                  >
                    {interests.map((interest) => (
                      <option key={interest} value={interest}>
                        {interest}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Message
                </label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  rows="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-metalogics-primary"
                  placeholder="Tell us about your project or what you'd like to discuss..."
                />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Choose your preferred time
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Preferred Date *
                  </label>
                  <input
                    type="date"
                    name="preferredDate"
                    value={formData.preferredDate}
                    onChange={handleInputChange}
                    min={new Date().toISOString().split("T")[0]}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-metalogics-primary"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Preferred Time *
                  </label>
                  <select
                    name="preferredTime"
                    value={formData.preferredTime}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-metalogics-primary"
                    required
                  >
                    <option value="">Select a time</option>
                    {timeSlots.map((time) => (
                      <option key={time} value={time}>
                        {time}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> All times are in UK time (GMT/BST).
                  We'll send you a calendar invite and confirmation email.
                </p>
              </div>
            </div>
          )}

          {step === 3 && submitted && (
            <div className="text-center py-8">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Demo Booked Successfully!
              </h3>
              <p className="text-gray-600 mb-4">
                We've sent a calendar invite to {formData.email}. You'll receive
                a confirmation email shortly.
              </p>
              <div className="bg-gray-50 p-4 rounded-lg text-left">
                <h4 className="font-medium text-gray-900 mb-2">
                  Booking Details:
                </h4>
                <p className="text-sm text-gray-600">
                  <strong>Name:</strong> {formData.name}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Date:</strong> {formData.preferredDate}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Time:</strong> {formData.preferredTime}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Interest:</strong> {formData.interest}
                </p>
              </div>
            </div>
          )}

          <div className="flex justify-between mt-6">
            {step > 1 && step < 3 && (
              <button
                onClick={prevStep}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Back
              </button>
            )}
            {step < 3 && !submitted && (
              <button
                onClick={step === 2 ? handleSubmit : nextStep}
                disabled={
                  loading ||
                  (step === 1 && (!formData.name || !formData.email)) ||
                  (step === 2 &&
                    (!formData.preferredDate || !formData.preferredTime))
                }
                className="px-6 py-2 bg-metalogics-primary text-white rounded-lg hover:bg-metalogics-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors ml-auto"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    Booking...
                  </>
                ) : step === 2 ? (
                  "Book Demo"
                ) : (
                  "Next"
                )}
              </button>
            )}
            {submitted && (
              <button
                onClick={onClose}
                className="px-6 py-2 bg-metalogics-primary text-white rounded-lg hover:bg-metalogics-primary/90 transition-colors ml-auto"
              >
                Close
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookingModal;
