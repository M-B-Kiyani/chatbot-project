import React from 'react';

const LinkButton = ({ linkData }) => {
  const { url, text, label, type } = linkData || {};

  if (!url) {
    return <div className="text-gray-600">Invalid link</div>;
  }

  const displayText = text || label || 'Click here';

  if (type === 'auth') {
    return (
      <div className="flex justify-center">
        <button
          onClick={() => window.location.href = url}
          className="inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          {displayText}
        </button>
      </div>
    );
  }

  return (
    <div className="flex justify-center">
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium"
      >
        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
        </svg>
        {displayText}
      </a>
    </div>
  );
};

export default LinkButton;