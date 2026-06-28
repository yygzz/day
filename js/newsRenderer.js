import { getCategoryImage, loadImageWithFallbacks } from './renderer.js';

const CATEGORY_GRADIENTS = {
  politics: 'linear-gradient(135deg, #1e212b 0%, #3a3f4b 100%)',
  conflict: 'linear-gradient(135deg, #2d1b1b 0%, #4a2f2f 100%)',
  economy: 'linear-gradient(135deg, #1b2d2a 0%, #2f4a45 100%)',
  technology: 'linear-gradient(135deg, #1b1f2d 0%, #2f354a 100%)',
  science: 'linear-gradient(135deg, #0f2e3a 0%, #1a4a5c 100%)',
  society: 'linear-gradient(135deg, #2d1b2e 0%, #4a2f4d 100%)',
  culture: 'linear-gradient(135deg, #3d2b1f 0%, #5e4b35 100%)',
  sports: 'linear-gradient(135deg, #1a2a3a 0%, #2d4a5e 100%)'
};

function categoryLabel(category) {
  const labels = {
    politics: '政治',
    conflict: '冲突',
    economy: '经济',
    technology: '科技',
    science: '科学',
    society: '社会',
    culture: '文化',
    sports: '体育'
  };
  return labels[category] || '国际';
}

const NEWS_CATEGORY_IMAGES = {
  politics: [
    'https://images.unsplash.com/photo-1540910419-d4734630c087?w=1920&q=80',
    'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1920&q=80',
    'https://images.unsplash.com/photo-1555848962-6e79363ec58f?w=1920&q=80',
    'https://images.unsplash.com/photo-1572949791660-6626e0e8d482?w=1920&q=80',
    'https://images.unsplash.com/photo-1523995462485-3d171b5c8fa9?w=1920&q=80',
    'https://images.unsplash.com/photo-1569025743873-ea3a9c52589b?w=1920&q=80'
  ],
  conflict: [
    'https://images.unsplash.com/photo-1580130379745-139975c7e62c?w=1920&q=80',
    'https://images.unsplash.com/photo-1558522195-e1201b090344?w=1920&q=80',
    'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1920&q=80',
    'https://images.unsplash.com/photo-1590073242676-cfea6866c272?w=1920&q=80',
    'https://images.unsplash.com/photo-1616423640778-28d1b53229bd?w=1920&q=80',
    'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1920&q=80'
  ],
  economy: [
    'https://images.unsplash.com/photo-1611974765270-ca12586343bb?w=1920&q=80',
    'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1920&q=80',
    'https://images.unsplash.com/photo-1611974765270-ca12586343bb?w=1920&q=80',
    'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=1920&q=80',
    'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&q=80',
    'https://images.unsplash.com/photo-1468254095679-bbcba94a7066?w=1920&q=80'
  ],
  technology: [
    'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=80',
    'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1920&q=80',
    'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80',
    'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1920&q=80',
    'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1920&q=80',
    'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&q=80'
  ],
  science: [
    'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80',
    'https://images.unsplash.com/photo-1446776811953-d23d52307f7a?w=1920&q=80',
    'https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=1920&q=80',
    'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1920&q=80',
    'https://images.unsplash.com/photo-1576086213369-97a306d36757?w=1920&q=80',
    'https://images.unsplash.com/photo-1507668077129-56e3f0907c17?w=1920&q=80'
  ],
  society: [
    'https://images.unsplash.com/photo-1569180882533-0642c64ebc6f?w=1920&q=80',
    'https://images.unsplash.com/photo-1491438590914-bc09fcaaf77a?w=1920&q=80',
    'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1920&q=80',
    'https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=1920&q=80',
    'https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?w=1920&q=80',
    'https://images.unsplash.com/photo-1576153192396-180ecef2a715?w=1920&q=80'
  ],
  culture: [
    'https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=1920&q=80',
    'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=1920&q=80',
    'https://images.unsplash.com/photo-1499781350541-7783f6c6a0c8?w=1920&q=80',
    'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=1920&q=80',
    'https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?w=1920&q=80',
    'https://images.unsplash.com/photo-1493225255756-d9584f8606e9?w=1920&q=80'
  ],
  sports: [
    'https://images.unsplash.com/photo-1517649763962-0c623066013b?w=1920&q=80',
    'https://images.unsplash.com/photo-1515523110800-9415d13b84a8?w=1920&q=80',
    'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=1920&q=80',
    'https://images.unsplash.com/photo-1560272564-c83b66b1ad12?w=1920&q=80',
    'https://images.unsplash.com/photo-1517927033932-b3d18e61fb3a?w=1920&q=80',
    'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1920&q=80'
  ]
};

function buildImageCandidates(item, index) {
  const category = item.category || 'politics';
  const candidates = [];
  if (item.image) candidates.push(item.image);
  const images = NEWS_CATEGORY_IMAGES[category] || NEWS_CATEGORY_IMAGES.politics;
  for (let i = 0; i < images.length; i++) {
    candidates.push(images[(index + i) % images.length]);
  }
  return candidates;
}

function createNewsCard(item, index, total) {
  const card = document.createElement('article');
  card.className = 'news-card';
  const category = item.category || 'politics';
  card.style.setProperty('--news-gradient', CATEGORY_GRADIENTS[category] || CATEGORY_GRADIENTS.politics);

  const candidates = buildImageCandidates(item, index);
  const metaParts = [
    item.time,
    item.location,
    item.people,
    item.source
  ].filter(Boolean);

  card.innerHTML = `
    <div class="news-card-bg"></div>
    <div class="news-card-overlay"></div>
    <div class="news-card-badges">
      <span class="news-badge reliability">可靠 ${item.reliability}/10</span>
      <span class="news-badge importance">重要 ${item.importance}/10</span>
    </div>
    <div class="news-card-content">
      <span class="news-card-category">${categoryLabel(category)}</span>
      <h2 class="news-card-title">${item.title}</h2>
      <p class="news-card-summary">${item.summary}</p>
      <p class="news-card-evaluation">${item.evaluation}</p>
      <div class="news-card-meta">
        ${metaParts.map((part, i) => `${i > 0 ? '<span class="dot">•</span>' : ''}${part}`).join('')}
      </div>
      <a class="news-card-link" href="${item.sourceUrl}" target="_blank" rel="noopener noreferrer">
        查看原文 ↗
      </a>
    </div>
  `;

  const bg = card.querySelector('.news-card-bg');
  loadImageWithFallbacks(bg, candidates);

  return card;
}

async function renderNews(container) {
  container.innerHTML = '';
  const response = await fetch('./data/news.json');
  if (!response.ok) {
    container.innerHTML = '<div class="news-view"><div class="news-track"><div class="news-card"><div class="news-card-content"><h2 class="news-card-title">新闻加载失败</h2></div></div></div></div>';
    return;
  }
  const data = await response.json();
  const items = data.news || [];

  const view = document.createElement('div');
  view.className = 'news-view';
  const track = document.createElement('div');
  track.className = 'news-track';

  items.forEach((item, index) => {
    track.appendChild(createNewsCard(item, index, items.length));
  });

  view.appendChild(track);
  container.appendChild(view);

  // 进度指示
  const progress = document.createElement('div');
  progress.className = 'news-progress';
  for (let i = 0; i < items.length; i++) {
    const dot = document.createElement('div');
    dot.className = 'news-progress-dot';
    dot.dataset.index = i;
    progress.appendChild(dot);
  }
  container.appendChild(progress);

  const updateDots = () => {
    const cardHeight = view.offsetHeight;
    const index = Math.round(view.scrollTop / cardHeight);
    progress.querySelectorAll('.news-progress-dot').forEach((dot, i) => {
      dot.classList.toggle('active', i === index);
    });
  };
  view.addEventListener('scroll', updateDots, { passive: true });
  updateDots();
}

export { renderNews };
