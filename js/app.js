import { getEventsForDate, getHolidaysForDate, formatDisplayDate, addDays } from './data.js';
import { renderEvents } from './renderer.js';

let currentDate = new Date();
const app = document.getElementById('app');
const dateLabel = document.getElementById('current-date');
const prevBtn = document.getElementById('prev-date');
const nextBtn = document.getElementById('next-date');
const holidaysBar = document.getElementById('holidays-bar');
const scrollHint = document.getElementById('scroll-hint');

async function loadDate(date) {
  currentDate = date;
  dateLabel.textContent = formatDisplayDate(date);

  const [events, holidays] = await Promise.all([
    getEventsForDate(date),
    getHolidaysForDate(date)
  ]);

  renderHolidays(holidays);

  // 切换日期时瞬时重置滚动，避免动画冲突
  app.scrollTop = 0;
  renderEvents(events, app);
  initScrollAnimations();
  updateActiveSection();
}

function renderHolidays(holidays) {
  holidaysBar.innerHTML = '';
  if (!holidays.length) {
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

prevBtn.addEventListener('click', () => loadDate(addDays(currentDate, -1)));
nextBtn.addEventListener('click', () => loadDate(addDays(currentDate, 1)));

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

  // 内容入场动画
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

  // 平滑吸附：根据滚动距离动态调整时长，避免生硬
  if (total > 1) {
    const track = createSnapTrack(total);
    const sectionHeight = getSectionHeight();
    const maxDuration = 0.55;

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
        duration: { min: 0.2, max: maxDuration },
        delay: 0,
        ease: 'power2.out'
      }
    });
  }
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
