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

function buildImageCandidates(item, index) {
  const category = item.category || 'politics';
  const candidates = [];
  if (item.image) candidates.push(item.image);
  const images = [
    'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1920&q=80',
    'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1920&q=80',
    'https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=1920&q=80',
    'https://images.unsplash.com/photo-1495020689067-958852a7765e?w=1920&q=80',
    'https://images.unsplash.com/photo-1555848962-6e79363ec58f?w=1920&q=80',
    'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80',
    'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=80',
    'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=1920&q=80'
  ];
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
  progress.textContent = `1 / ${items.length}`;
  container.appendChild(progress);

  view.addEventListener('scroll', () => {
    const cardHeight = view.offsetHeight;
    const index = Math.round(view.scrollTop / cardHeight) + 1;
    progress.textContent = `${Math.min(index, items.length)} / ${items.length}`;
  }, { passive: true });
}

export { renderNews };
