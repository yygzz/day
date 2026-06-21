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
  renderEvents(events, app);
  app.scrollTo({ top: 0, behavior: 'smooth' });
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

    const enterTl = gsap.timeline({
      scrollTrigger: {
        trigger: section,
        scroller: '#app',
        start: 'top bottom',
        end: 'center center',
        scrub: 0.5,
      }
    });

    enterTl.fromTo(bg, { scale: 1.15 }, { scale: 1.0, ease: 'none' }, 0);
    enterTl.fromTo(title, { y: 60, opacity: 0 }, { y: 0, opacity: 1, ease: 'none' }, 0);
    if (desc) enterTl.fromTo(desc, { y: 40, opacity: 0 }, { y: 0, opacity: 1, ease: 'none' }, 0.1);
    if (meta) enterTl.fromTo(meta, { y: 20, opacity: 0 }, { y: 0, opacity: 1, ease: 'none' }, 0);
    if (watermark) enterTl.fromTo(watermark, { y: 80, opacity: 0 }, { y: 0, opacity: 0.08, ease: 'none' }, 0);

    const exitTl = gsap.timeline({
      scrollTrigger: {
        trigger: section,
        scroller: '#app',
        start: 'center center',
        end: 'bottom top',
        scrub: 0.5,
      }
    });

    exitTl.to([title, desc, meta].filter(Boolean), { y: -60, opacity: 0, ease: 'none' }, 0);
    exitTl.to(bg, { filter: 'blur(4px)', ease: 'none' }, 0);
  });
}

function updateActiveSection() {
  const sections = document.querySelectorAll('.event-section');
  const appRect = app.getBoundingClientRect();
  const centerY = appRect.top + appRect.height / 2;

  sections.forEach(section => {
    const rect = section.getBoundingClientRect();
    const sectionCenter = rect.top + rect.height / 2;
    if (Math.abs(sectionCenter - centerY) < rect.height / 2) {
      section.classList.add('active');
    } else {
      section.classList.remove('active');
    }
  });
}

function initMouseParallax() {
  document.addEventListener('mousemove', (e) => {
    const x = (e.clientX / window.innerWidth - 0.5) * 2;
    const y = (e.clientY / window.innerHeight - 0.5) * 2;

    const activeBg = document.querySelector('.event-section.active .event-bg');
    if (!activeBg) return;

    if (typeof gsap !== 'undefined') {
      gsap.to(activeBg, {
        x: -x * 15,
        y: -y * 15,
        duration: 0.6,
        ease: 'power2.out'
      });
    }
  });
}

function scrollToNextSection() {
  const sectionHeight = window.innerHeight;
  const nextIndex = Math.round(app.scrollTop / sectionHeight) + 1;
  const maxIndex = document.querySelectorAll('.event-section').length - 1;
  app.scrollTo({ top: Math.min(nextIndex, maxIndex) * sectionHeight, behavior: 'smooth' });
}

function scrollToPrevSection() {
  const sectionHeight = window.innerHeight;
  const prevIndex = Math.round(app.scrollTop / sectionHeight) - 1;
  app.scrollTo({ top: Math.max(0, prevIndex) * sectionHeight, behavior: 'smooth' });
}

app.addEventListener('scroll', () => {
  requestAnimationFrame(updateActiveSection);
});

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
