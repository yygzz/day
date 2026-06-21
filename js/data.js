const EVENTS_URL = './data/events.json';

function formatDate(date) {
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${m}-${d}`;
}

function formatDisplayDate(date) {
  return `${date.getFullYear()} 年 ${date.getMonth() + 1} 月 ${date.getDate()} 日`;
}

function addDays(date, days) {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

async function fetchEvents() {
  const response = await fetch(EVENTS_URL);
  if (!response.ok) {
    throw new Error(`Failed to load events: ${response.status}`);
  }
  const data = await response.json();
  return data.events || [];
}

async function getEventsForDate(date) {
  const allEvents = await fetchEvents();
  const key = formatDate(date);
  return allEvents.filter(ev => ev.date === key);
}

export { formatDate, formatDisplayDate, addDays, fetchEvents, getEventsForDate };
