const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export const postChat = async (message, sessionId) => {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, sessionId }),
  });
  if (!response.ok) throw new Error('Failed to post chat');
  return await response.json();
};

export const scheduleCheck = async (payload) => {
  const response = await fetch(`${API_BASE_URL}/api/schedule-check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error('Failed to check schedule');
  return await response.json();
};

export const createBooking = async (payload) => {
  const response = await fetch(`${API_BASE_URL}/api/create-booking`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error('Failed to create booking');
  return await response.json();
};

export const ragSearch = async (q, n_results) => {
  const response = await fetch(`${API_BASE_URL}/api/rag-search?q=${encodeURIComponent(q)}&n_results=${n_results}`);
  if (!response.ok) throw new Error('Failed to search RAG');
  return await response.json();
};

export const getPricing = async (service) => {
  const response = await fetch(`${API_BASE_URL}/api/pricing?service=${encodeURIComponent(service)}`);
  if (!response.ok) throw new Error('Failed to get pricing');
  return await response.json();
};

export const getCalendarAuth = async () => {
  const response = await fetch(`${API_BASE_URL}/api/calendar/auth`);
  if (!response.ok) throw new Error('Failed to get calendar auth');
  return await response.json();
};