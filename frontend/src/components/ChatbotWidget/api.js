const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = {
  async chat(message) {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    if (!response.ok) throw new Error('Chat API failed');
    return response.json();
  },

  async ragSearch(query) {
    const response = await fetch(`${API_BASE_URL}/api/rag-search?q=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error('RAG Search API failed');
    return response.json();
  },

  async scheduleCheck(data) {
    const response = await fetch(`${API_BASE_URL}/api/schedule-check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Schedule Check API failed');
    return response.json();
  },

  async createBooking(data) {
    const payload = {
      user: 'user', // placeholder
      start: data.time,
      duration: data.duration,
      summary: 'Chatbot Booking',
      description: 'Booking created via chatbot',
      calendar_id: 'primary',
      timezone: 'UTC'
    };
    const response = await fetch(`${API_BASE_URL}/api/create-booking`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error('Create Booking API failed');
    return response.json();
  },

  async getPricing(service) {
    const response = await fetch(`${API_BASE_URL}/api/pricing?service=${encodeURIComponent(service)}`);
    if (!response.ok) throw new Error('Pricing API failed');
    return response.json();
  },

  calendarAuth() {
    window.open(`${API_BASE_URL}/api/calendar/auth`, '_blank', 'noopener');
  },

  hubspotAuth() {
    window.open(`${API_BASE_URL}/api/hubspot/auth`, '_blank', 'noopener');
  }
};