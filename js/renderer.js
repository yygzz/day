function createEventSection(event, index, total) {
  const section = document.createElement('section');
  section.className = 'event-section';
  section.dataset.index = index;
  section.style.setProperty('--event-gradient', event.theme.gradient);

  const textColorClass = event.theme.textColor === 'dark' ? 'text-dark' : 'text-light';
  section.classList.add(textColorClass);

  section.innerHTML = `
    <div class="event-bg" style="background-image: url('${event.image}')"></div>
    <div class="event-overlay"></div>
    <div class="event-content">
      <div class="event-meta">${event.year} · ${categoryLabel(event.category)}</div>
      <h1 class="event-title">${event.title}</h1>
      <p class="event-description">${event.description}</p>
    </div>
    <div class="event-year-watermark">${event.year}</div>
    <div class="event-progress">事件 ${index + 1} / ${total}</div>
  `;

  return section;
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
        <h1 class="event-title">这一天还没有收录事件</h1>
        <p class="event-description">试试切换日期，或者回来再看看。我们会在后续补充更多国际重要日子。</p>
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
}

export { renderEvents };
