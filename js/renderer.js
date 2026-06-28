const CATEGORY_IMAGES = {
  technology: [
    'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=80',
    'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1920&q=80',
    'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=80',
    'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80',
    'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1920&q=80',
    'https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=1920&q=80',
    'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=1920&q=80',
    'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1920&q=80'
  ],
  science: [
    'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80',
    'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=1920&q=80',
    'https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=1920&q=80',
    'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1920&q=80',
    'https://images.unsplash.com/photo-1446776811953-d23d52307f7a?w=1920&q=80',
    'https://images.unsplash.com/photo-1576086213369-97a306d36757?w=1920&q=80',
    'https://images.unsplash.com/photo-1507668077129-56e3f0907c17?w=1920&q=80',
    'https://images.unsplash.com/photo-1518152006812-ed8ddde498f1?w=1920&q=80'
  ],
  culture: [
    'https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=1920&q=80',
    'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=1920&q=80',
    'https://images.unsplash.com/photo-1499781350541-7783f6c6a0c8?w=1920&q=80',
    'https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=1920&q=80',
    'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=1920&q=80',
    'https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?w=1920&q=80',
    'https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=1920&q=80',
    'https://images.unsplash.com/photo-1493225255756-d9584f8606e9?w=1920&q=80'
  ],
  holiday: [
    'https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=1920&q=80',
    'https://images.unsplash.com/photo-1544367563-12123d8965cd?w=1920&q=80',
    'https://images.unsplash.com/photo-1467810563316-b5476525c0f9?w=1920&q=80',
    'https://images.unsplash.com/photo-1512389142860-9c449e58a543?w=1920&q=80',
    'https://images.unsplash.com/photo-1519671482-2c208eb93f21?w=1920&q=80',
    'https://images.unsplash.com/photo-1482517967863-00e15c9b44be?w=1920&q=80',
    'https://images.unsplash.com/photo-1527529482837-4698179dc6ce?w=1920&q=80',
    'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=1920&q=80'
  ],
  society: [
    'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1920&q=80',
    'https://images.unsplash.com/photo-1569180882533-0642c64ebc6f?w=1920&q=80',
    'https://images.unsplash.com/photo-1576153192396-180ecef2a715?w=1920&q=80',
    'https://images.unsplash.com/photo-1523995462485-3d171b5c8fa9?w=1920&q=80',
    'https://images.unsplash.com/photo-1491438590914-bc09fcaaf77a?w=1920&q=80',
    'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1920&q=80',
    'https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=1920&q=80',
    'https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?w=1920&q=80'
  ],
  sports: [
    'https://images.unsplash.com/photo-1517649763962-0c623066013b?w=1920&q=80',
    'https://images.unsplash.com/photo-1515523110800-9415d13b84a8?w=1920&q=80',
    'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1920&q=80',
    'https://images.unsplash.com/photo-1461896836934-3f65726f5cd0?w=1920&q=80',
    'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=1920&q=80',
    'https://images.unsplash.com/photo-1560272564-c83b66b1ad12?w=1920&q=80',
    'https://images.unsplash.com/photo-1517927033932-b3d18e61fb3a?w=1920&q=80',
    'https://images.unsplash.com/photo-1461896836934-3f65726f5cd0?w=1920&q=80'
  ],
  politics: [
    'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1920&q=80',
    'https://images.unsplash.com/photo-1555848962-6e79363ec58f?w=1920&q=80',
    'https://images.unsplash.com/photo-1572949791660-6626e0e8d482?w=1920&q=80',
    'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1920&q=80',
    'https://images.unsplash.com/photo-1523995462485-3d171b5c8fa9?w=1920&q=80',
    'https://images.unsplash.com/photo-1551817958-c5c465be798f?w=1920&q=80',
    'https://images.unsplash.com/photo-1569025743873-ea3a9c52589b?w=1920&q=80',
    'https://images.unsplash.com/photo-1540910419-d4734630c087?w=1920&q=80'
  ]
};

const CATEGORY_GRADIENTS = {
  technology: 'linear-gradient(135deg, #1e212b 0%, #3a3f4b 100%)',
  science: 'linear-gradient(135deg, #0f2e3a 0%, #1a4a5c 100%)',
  culture: 'linear-gradient(135deg, #3d2b1f 0%, #5e4b35 100%)',
  holiday: 'linear-gradient(135deg, #1a3a2a 0%, #2d5a45 100%)',
  society: 'linear-gradient(135deg, #2d1b2e 0%, #4a2f4d 100%)',
  sports: 'linear-gradient(135deg, #1a2a3a 0%, #2d4a5e 100%)',
  politics: 'linear-gradient(135deg, #2d1b2e 0%, #4a2f4d 100%)'
};

function getCategoryImage(category, index = 0) {
  const images = CATEGORY_IMAGES[category] || CATEGORY_IMAGES.politics;
  return images[index % images.length];
}

function getCategoryGradient(category) {
  return CATEGORY_GRADIENTS[category] || CATEGORY_GRADIENTS.politics;
}

function buildImageCandidates(event, index) {
  const category = event.category || 'politics';
  const candidates = [];
  if (event.image) candidates.push(event.image);
  const images = CATEGORY_IMAGES[category] || CATEGORY_IMAGES.politics;
  for (let i = 0; i < images.length; i++) {
    candidates.push(images[(index + i) % images.length]);
  }
  // Last resort: any category
  if (!CATEGORY_IMAGES[category]) {
    candidates.push(...CATEGORY_IMAGES.politics);
  }
  return candidates;
}

function createEventSection(event, index, total) {
  const section = document.createElement('section');
  section.className = 'event-section';
  section.dataset.index = index;

  const category = event.category || 'politics';
  const gradient = event.theme?.gradient || getCategoryGradient(category);
  section.style.setProperty('--event-gradient', gradient);

  const textColorClass = event.theme?.textColor === 'dark' ? 'text-dark' : 'text-light';
  section.classList.add(textColorClass);

  const candidates = buildImageCandidates(event, index);
  const imageUrl = candidates[0];

  section.innerHTML = `
    <div class="event-bg" data-candidates='${JSON.stringify(candidates)}'></div>
    <div class="event-overlay"></div>
    <div class="event-content">
      <div class="event-meta"><span>${event.year || '历史'}</span><span>${categoryLabel(category)}</span></div>
      <h1 class="event-title">${event.title}</h1>
      <p class="event-description">${event.description}</p>
    </div>
    <div class="event-year-watermark">${event.year || ''}</div>
  `;

  const bg = section.querySelector('.event-bg');
  loadImageWithFallbacks(bg, candidates);

  return section;
}

function loadImageWithFallbacks(element, candidates, attempt = 0) {
  if (attempt >= candidates.length) {
    // All failed: keep gradient background, mark loaded so text appears
    element.classList.add('loaded');
    return;
  }

  const attemptKey = `attempt-${attempt}`;
  element.dataset.currentAttempt = attemptKey;
  const url = candidates[attempt];
  const img = new Image();
  img.src = url;

  img.onload = () => {
    if (element.dataset.currentAttempt !== attemptKey) return;
    element.style.backgroundImage = `url('${url}')`;
    element.classList.add('loaded');
    element.dataset.currentAttempt = 'done';
  };

  img.onerror = () => {
    if (element.dataset.currentAttempt !== attemptKey) return;
    loadImageWithFallbacks(element, candidates, attempt + 1);
  };

  // Timeout safeguard for very slow loads
  setTimeout(() => {
    if (element.dataset.currentAttempt !== attemptKey) return;
    img.src = '';
    loadImageWithFallbacks(element, candidates, attempt + 1);
  }, 6000);
}

function preloadNextImages(events, startIndex, count = 3) {
  for (let i = startIndex + 1; i <= startIndex + count && i < events.length; i++) {
    const event = events[i];
    const candidates = buildImageCandidates(event, i);
    const img = new Image();
    img.src = candidates[0];
  }
}

function categoryLabel(category) {
  const labels = {
    technology: '科技里程碑',
    science: '科学突破',
    culture: '文化艺术',
    holiday: '国际节日',
    society: '社会运动',
    sports: '体育时刻',
    politics: '政治变革'
  };
  return labels[category] || '历史时刻';
}

function renderEmptyState(container) {
  container.innerHTML = `
    <section class="event-section" style="--event-gradient: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)">
      <div class="event-overlay"></div>
      <div class="event-content">
        <div class="event-meta">暂无记录</div>
        <h1 class="event-title">这一天尚未收录事件</h1>
        <p class="event-description">换个日期试试，更多国际重要日子正在补充中。</p>
      </div>
    </section>
  `;
}

function renderEvents(events, container) {
  container.innerHTML = '';
  if (events.length === 0) {
    renderEmptyState(container);
    return;
  }
  const total = events.length;
  events.forEach((event, index) => {
    const section = createEventSection(event, index, total);
    container.appendChild(section);
  });

  const progress = document.createElement('div');
  progress.className = 'event-progress';
  progress.id = 'event-progress';
  for (let i = 0; i < total; i++) {
    const dot = document.createElement('div');
    dot.className = 'event-progress-dot';
    dot.dataset.index = i;
    progress.appendChild(dot);
  }
  container.appendChild(progress);

  preloadNextImages(events, 0, 3);
}

export { renderEvents, getCategoryImage, getCategoryGradient, preloadNextImages, loadImageWithFallbacks };
