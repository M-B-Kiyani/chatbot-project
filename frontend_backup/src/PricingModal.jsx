import React, { useState, useEffect } from "react";
import { X, CheckCircle, Loader2 } from "lucide-react";

const PricingModal = ({ isOpen, onClose }) => {
  const [pricingData, setPricingData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedService, setSelectedService] = useState("web-development");

  const services = [
    { id: "web-development", name: "Web Development" },
    { id: "seo", name: "SEO Optimization" },
    { id: "graphic-design", name: "Graphic Design" },
  ];

  useEffect(() => {
    if (isOpen && selectedService) {
      fetchPricing();
    }
  }, [isOpen, selectedService]);

  const fetchPricing = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/pricing?service=${selectedService}`
      );
      if (response.ok) {
        const data = await response.json();
        setPricingData(data);
      }
    } catch (error) {
      console.error("Error fetching pricing:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">
              Pricing Information
            </h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Service Selector */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Service
            </label>
            <select
              value={selectedService}
              onChange={(e) => setSelectedService(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-metalogics-primary"
            >
              {services.map((service) => (
                <option key={service.id} value={service.id}>
                  {service.name}
                </option>
              ))}
            </select>
          </div>

          {/* Pricing Content */}
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-metalogics-primary" />
              <span className="ml-2 text-gray-600">Loading pricing...</span>
            </div>
          ) : pricingData ? (
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {pricingData.service.replace("-", " ").toUpperCase()}
                </h3>
                <p className="text-gray-600">
                  Choose the package that fits your needs
                </p>
              </div>

              <div className="grid gap-4">
                {pricingData.duration_options.map((option, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-6 hover:border-metalogics-primary transition-colors"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-lg font-semibold text-gray-900">
                        {option.duration}
                      </h4>
                      <div className="text-2xl font-bold text-metalogics-primary">
                        £{option.price}
                      </div>
                    </div>
                    <div className="text-sm text-gray-600 mb-3">
                      {option.breakdown}
                    </div>
                    <button className="w-full bg-gradient-to-r from-metalogics-primary to-metalogics-secondary text-white py-2 px-4 rounded-lg font-medium hover:shadow-lg transition-all duration-300 transform hover:scale-105">
                      {pricingData.default_cta}
                    </button>
                  </div>
                ))}
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 text-center">
                  All prices are in GBP and include VAT. Custom quotes available
                  for larger projects.
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600">
                Unable to load pricing information. Please try again.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PricingModal;
