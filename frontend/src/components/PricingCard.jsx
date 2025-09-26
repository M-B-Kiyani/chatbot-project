import React from 'react';

const PricingCard = ({ pricingData, onSelect }) => {
  if (!pricingData || !pricingData.duration_options) {
    return <div className="text-gray-600">Loading pricing information...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {pricingData.service.replace("-", " ").toUpperCase()}
        </h3>
        <p className="text-gray-600 text-sm">
          Choose the package that fits your needs
        </p>
      </div>

      <div className="grid gap-3">
        {pricingData.duration_options.map((option, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-500 transition-colors"
          >
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-md font-semibold text-gray-900">
                {option.duration}
              </h4>
              <div className="text-xl font-bold text-blue-600">
                £{option.price}
              </div>
            </div>
            <div className="text-sm text-gray-600 mb-3">
              {option.breakdown}
            </div>
            <button
              onClick={() => onSelect && onSelect(`I want the ${option.duration} package`)}
              className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:shadow-lg transition-all duration-300 text-sm"
            >
              {pricingData.default_cta}
            </button>
          </div>
        ))}
      </div>

      <div className="bg-gray-50 p-3 rounded-lg">
        <p className="text-xs text-gray-600 text-center">
          All prices are in GBP and include VAT. Custom quotes available for larger projects.
        </p>
      </div>
    </div>
  );
};

export default PricingCard;