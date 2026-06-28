import { getEventsForDate, getHolidaysForDate, formatDisplayDate, addDays } from './data.js';
import { renderEvents } from './renderer.js';
import { renderNews } from './newsRenderer.js';

let currentDate = new Date();
let currentView = 'history';
const app = document.getElementById('app');
const dateLabel = document.getElementById('current-date');
const prevBtn = document.getElementById('prev-date');
const nextBtn = document.getElementById('next-date');
const holidaysBar = document.getElementById('holidays-bar');
const scrollHint = document.getElementById('scroll-hint');
const tabBtns = document.querySelectorAll('.tab-btn');
const tabsContainer = document.querySelector('.section-tabs');
const dateControls = document.querySelector('.date-controls');
const datePicker = document.getElementById('date-picker');
const todayBtn = document.getElementById('today-btn');

async function loadDate(date) {
  currentDate = date;
  dateLabel.textContent = formatDisplayDate(date);

  const [events, holidays] = await Promise.all([
    getEventsForDate(date),
    getHolidaysForDate(date)
  ]);

  renderHolidays(holidays);
  syncDatePicker(currentDate);

  app.scrollTop = 0;
  renderEvents(events, app);
  initScrollAnimations();
  updateActiveSection();
}

function renderHolidays(holidays) {
  holidaysBar.innerHTML = '';
  if (!holidays.length || currentView !== 'history') {
    holidaysBar.classList.remove('visible');
    return;
  }

  holidays.forEach(h => {
    const chip = document.createElement('span');
    chip.className = 'holiday-chip';
    chip.textContent = h.name;
    chip.title = h.en;
    holidaysBar.appendChild(chip);
  });

  holidaysBar.classList.add('visible');
}

function syncDatePicker(date) {
  if (!datePicker) return;
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  datePicker.value = `${y}-${m}-${d}`;
}

prevBtn.addEventListener('click', () => loadDate(addDays(currentDate, -1)));
nextBtn.addEventListener('click', () => loadDate(addDays(currentDate, 1)));
todayBtn.addEventListener('click', () => loadDate(new Date()));

datePicker.addEventListener('change', (e) => {
  const value = e.target.value;
  if (!value) return;
  loadDate(new Date(value + 'T00:00:00'));
});

tabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const view = btn.dataset.view;
    if (view === currentView) return;
    switchView(view);
  });
});

function switchView(view) {
  currentView = view;

  tabBtns.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.view === view);
  });

  if (tabsContainer) {
    tabsContainer.setAttribute('data-active', view);
  }

  if (view === 'history') {
    dateControls.style.display = '';
    loadDate(currentDate);
    if (scrollHint) scrollHint.classList.remove('hidden');
  } else {
    dateControls.style.display = 'none';
    holidaysBar.classList.remove('visible');
    app.innerHTML = '';
    renderNews(app);
    if (scrollHint) scrollHint.classList.add('hidden');
    // 隐藏滚动提示的滚动监听重置
  }
}

function createSnapTrack(totalSections) {
  let track = document.getElementById('snap-track');
  if (!track) {
    track = document.createElement('div');
    track.id = 'snap-track';
    track.style.cssText = 'position:absolute;top:0;left:0;width:1px;pointer-events:none;z-index:-1;';
    app.appendChild(track);
  }
  const sectionHeight = getSectionHeight();
  track.style.height = `${totalSections * sectionHeight}px`;
  return track;
}

function initScrollAnimations() {
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
    return;
  }

  gsap.registerPlugin(ScrollTrigger);
  ScrollTrigger.getAll().forEach(t => t.kill());

  const sections = document.querySelectorAll('.event-section');
  const total = sections.length;

  if (total === 0) return;

  sections.forEach((section) => {
    const title = section.querySelector('.event-title');
    const desc = section.querySelector('.event-description');
    const meta = section.querySelector('.event-meta');
    const watermark = section.querySelector('.event-year-watermark');

    if (!title) return;

    gsap.set([title, desc, meta].filter(Boolean), { y: 40, opacity: 0 });
    if (watermark) gsap.set(watermark, { y: 60, opacity: 0 });

    gsap.to([title, desc, meta].filter(Boolean), {
      y: 0,
      opacity: 1,
      duration: 0.8,
      stagger: 0.08,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: section,
        scroller: '#app',
        start: 'top 75%',
        end: 'top 25%',
        toggleActions: 'play none none reverse'
      }
    });

    if (watermark) {
      gsap.to(watermark, {
        y: 0,
        opacity: 0.08,
        duration: 0.9,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: section,
          scroller: '#app',
          start: 'top 75%',
          end: 'top 25%',
          toggleActions: 'play none none reverse'
        }
      });
    }
  });

  if (total > 1) {
    const track = createSnapTrack(total);

    ScrollTrigger.create({
      trigger: track,
      scroller: '#app',
      start: 'top top',
      end: 'bottom bottom',
      snap: {
        snapTo: (progress) => {
          const snap = 1 / (total - 1);
          return Math.round(progress / snap) * snap;
        },
        duration: { min: 0.2, max: 0.55 },
        delay: 0,
        ease: 'power2.out'
      }
    });
  }
}

function updateActiveSection() {
  if (currentView !== 'history') return;
  const sections = document.querySelectorAll('.event-section');
  const dots = document.querySelectorAll('.event-progress-dot');
  const appRect = app.getBoundingClientRect();
  const centerY = appRect.top + appRect.height / 2;

  let activeIndex = 0;
  sections.forEach((section, index) => {
    const rect = section.getBoundingClientRect();
    const sectionCenter = rect.top + rect.height / 2;
    const isActive = Math.abs(sectionCenter - centerY) < rect.height / 2;
    section.classList.toggle('active', isActive);
    if (isActive) activeIndex = index;
  });

  dots.forEach((dot, index) => {
    dot.classList.toggle('active', index === activeIndex);
  });
}

function initMouseParallax() {
  let lastMove = 0;
  document.addEventListener('mousemove', (e) => {
    const now = Date.now();
    if (now - lastMove < 50) return;
    lastMove = now;

    if (currentView !== 'history') return;

    const x = (e.clientX / window.innerWidth - 0.5) * 2;
    const y = (e.clientY / window.innerHeight - 0.5) * 2;

    const activeBg = document.querySelector('.event-section.active .event-bg');
    if (!activeBg || !activeBg.classList.contains('loaded')) return;

    if (typeof gsap !== 'undefined') {
      gsap.to(activeBg, {
        x: -x * 10,
        y: -y * 10,
        duration: 0.9,
        ease: 'power2.out'
      });
    }
  });
}

function getSectionHeight() {
  const section = document.querySelector('.event-section');
  return section ? section.offsetHeight : window.innerHeight;
}

function scrollToNextSection() {
  if (currentView !== 'history') return;
  const sectionHeight = getSectionHeight();
  const nextIndex = Math.round(app.scrollTop / sectionHeight) + 1;
  const maxIndex = document.querySelectorAll('.event-section').length - 1;
  app.scrollTo({ top: Math.min(nextIndex, maxIndex) * sectionHeight, behavior: 'smooth' });
}

function scrollToPrevSection() {
  if (currentView !== 'history') return;
  const sectionHeight = getSectionHeight();
  const prevIndex = Math.round(app.scrollTop / sectionHeight) - 1;
  app.scrollTo({ top: Math.max(0, prevIndex) * sectionHeight, behavior: 'smooth' });
}

let scrollRaf = null;
app.addEventListener('scroll', () => {
  if (scrollRaf) return;
  scrollRaf = requestAnimationFrame(() => {
    updateActiveSection();
    scrollRaf = null;
  });
}, { passive: true });

document.addEventListener('keydown', (e) => {
  if (currentView !== 'history') return;
  if (e.key === 'ArrowDown' || e.key === 'PageDown') {
    e.preventDefault();
    scrollToNextSection();
    hideScrollHint();
  } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
    e.preventDefault();
    scrollToPrevSection();
    hideScrollHint();
  }
});

function hideScrollHint() {
  if (scrollHint) scrollHint.classList.add('hidden');
}

app.addEventListener('scroll', hideScrollHint, { once: true, passive: true });

let resizeTimer = null;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    const track = document.getElementById('snap-track');
    const total = document.querySelectorAll('.event-section').length;
    if (track && total > 0) {
      track.style.height = `${total * getSectionHeight()}px`;
    }
    if (typeof ScrollTrigger !== 'undefined') {
      ScrollTrigger.refresh();
    }
  }, 150);
});

initMouseParallax();
loadDate(currentDate);
