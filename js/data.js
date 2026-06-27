const EVENTS_URL = './data/events.json';
const HOLIDAYS_URL = './data/holidays.json';

let eventsCache = null;
let holidaysCache = null;

function formatDate(date) {
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${m}-${d}`;
}

function formatDisplayDate(date) {
  return `${date.getFullYear()} 年 ${date.getMonth() + 1} 月 ${date.getDate()} 日`;
}

function formatShortDate(date) {
  return `${date.getMonth() + 1} 月 ${date.getDate()} 日`;
}

function addDays(date, days) {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

async function fetchEvents() {
  if (eventsCache) return eventsCache;
  const response = await fetch(EVENTS_URL);
  if (!response.ok) {
    throw new Error(`Failed to load events: ${response.status}`);
  }
  const data = await response.json();
  eventsCache = data.events || [];
  return eventsCache;
}

async function fetchHolidays() {
  if (holidaysCache) return holidaysCache;
  try {
    const response = await fetch(HOLIDAYS_URL);
    if (!response.ok) return [];
    const data = await response.json();
    holidaysCache = data.holidays || [];
  } catch (e) {
    holidaysCache = [];
  }
  return holidaysCache;
}

async function getEventsForDate(date) {
  const allEvents = await fetchEvents();
  const key = formatDate(date);
  return allEvents.filter(ev => ev.date === key);
}

async function getHolidaysForDate(date) {
  const allHolidays = await fetchHolidays();
  const key = formatDate(date);
  return allHolidays.filter(h => h.date === key);
}

export { formatDate, formatDisplayDate, formatShortDate, addDays, fetchEvents, fetchHolidays, getEventsForDate, getHolidaysForDate };
