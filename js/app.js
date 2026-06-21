import { getEventsForDate, formatDisplayDate, addDays } from './data.js';
import { renderEvents } from './renderer.js';

let currentDate = new Date();
const app = document.getElementById('app');
const dateLabel = document.getElementById('current-date');
const prevBtn = document.getElementById('prev-date');
const nextBtn = document.getElementById('next-date');

async function loadDate(date) {
  currentDate = date;
  dateLabel.textContent = formatDisplayDate(date);
  const events = await getEventsForDate(date);

  // Instant reset avoids scroll-snap fighting with smooth scroll during re-render
  app.scrollTop = 0;
  renderEvents(events, app);
  initScrollAnimations();
  updateActiveSection();
}

prevBtn.addEventListener('click', () => loadDate(addDays(currentDate, -1)));
nextBtn.addEventListener('click', () => loadDate(addDays(currentDate, 1)));

function initScrollAnimations() {
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
    return;
  }

  gsap.registerPlugin(ScrollTrigger);
  ScrollTrigger.getAll().forEach(t => t.kill());

  const sections = document.querySelectorAll('.event-section');

  sections.forEach((section) => {
    const bg = section.querySelector('.event-bg');
    const title = section.querySelector('.event-title');
    const desc = section.querySelector('.event-description');
    const meta = section.querySelector('.event-meta');
    const watermark = section.querySelector('.event-year-watermark');

    if (!bg || !title) return;

    // Set initial states for a smooth entrance
    gsap.set([title, desc, meta].filter(Boolean), { y: 40, opacity: 0 });
    if (watermark) gsap.set(watermark, { y: 60, opacity: 0 });

    // Entrance: fade/slide content up when section reaches center
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
}

function updateActiveSection() {
  const sections = document.querySelectorAll('.event-section');
  const appRect = app.getBoundingClientRect();
  const centerY = appRect.top + appRect.height / 2;

  sections.forEach(section => {
    const rect = section.getBoundingClientRect();
    const sectionCenter = rect.top + rect.height / 2;
    const isActive = Math.abs(sectionCenter - centerY) < rect.height / 2;
    section.classList.toggle('active', isActive);
  });
}

function initMouseParallax() {
  let lastMove = 0;
  document.addEventListener('mousemove', (e) => {
    const now = Date.now();
    if (now - lastMove < 50) return;
    lastMove = now;

    const x = (e.clientX / window.innerWidth - 0.5) * 2;
    const y = (e.clientY / window.innerHeight - 0.5) * 2;

    const activeBg = document.querySelector('.event-section.active .event-bg');
    if (!activeBg || !activeBg.classList.contains('loaded')) return;

    if (typeof gsap !== 'undefined') {
      gsap.to(activeBg, {
        x: -x * 12,
        y: -y * 12,
        duration: 0.8,
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
  const sectionHeight = getSectionHeight();
  const nextIndex = Math.round(app.scrollTop / sectionHeight) + 1;
  const maxIndex = document.querySelectorAll('.event-section').length - 1;
  app.scrollTo({ top: Math.min(nextIndex, maxIndex) * sectionHeight, behavior: 'smooth' });
}

function scrollToPrevSection() {
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
  if (e.key === 'ArrowDown' || e.key === 'PageDown') {
    e.preventDefault();
    scrollToNextSection();
  } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
    e.preventDefault();
    scrollToPrevSection();
  }
});

initMouseParallax();
loadDate(currentDate);
