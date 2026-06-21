# On This Day 网站实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现一个静态网站，每天展示 3-5 个国际重要日子，每个事件占满一屏，支持上下滚动切换、自动吸附、视差动画和鼠标交互。

**Architecture:** 纯静态前端（HTML/CSS/JS）直接读取本地 `data/events.json`，按日期索引事件。使用 CSS scroll-snap 实现滚动吸附，GSAP + ScrollTrigger 实现华丽动画，原生 JS 监听鼠标移动产生视差。无需构建工具，直接浏览器打开 `index.html` 即可运行。

**Tech Stack:** HTML5, CSS3, JavaScript (ES6), GSAP + ScrollTrigger (CDN), Google Fonts (Inter / Noto Sans SC)

---

## 文件结构

```
/workspace/
├── index.html              # 页面入口，引入样式和脚本
├── css/
│   └── style.css           # 全局样式、事件区块样式、动画关键帧
├── js/
│   ├── data.js             # 数据层：读取 events.json，按日期过滤，日期工具函数
│   ├── renderer.js         # 渲染层：生成 EventSection DOM
│   └── app.js              # 应用层：初始化、滚动动画、鼠标视差、键盘/日期导航
└── data/
    └── events.json         # 事件数据源
```

---

### Task 1: 创建项目目录结构

**Files:**
- Create: `/workspace/index.html`
- Create: `/workspace/css/style.css`
- Create: `/workspace/js/data.js`
- Create: `/workspace/js/renderer.js`
- Create: `/workspace/js/app.js`
- Create: `/workspace/data/events.json`

- [ ] **Step 1: 创建目录和空文件**

```bash
mkdir -p /workspace/css /workspace/js /workspace/data
touch /workspace/index.html /workspace/css/style.css /workspace/js/data.js /workspace/js/renderer.js /workspace/js/app.js /workspace/data/events.json
```

- [ ] **Step 2: 验证目录结构**

Run: `find /workspace -maxdepth 2 -type f | sort`
Expected:
```
/workspace/css/style.css
/workspace/data/events.json
/workspace/index.html
/workspace/js/app.js
/workspace/js/data.js
/workspace/js/renderer.js
```

---

### Task 2: 填充初始事件数据

**Files:**
- Modify: `/workspace/data/events.json`

- [ ] **Step 1: 写入 6 月 21 日的示例事件数据**

```json
{
  "events": [
    {
      "id": "manchester-baby-1948",
      "date": "06-21",
      "year": 1948,
      "title": "“小婴儿”计算机首次成功运行",
      "description": "曼彻斯特“小婴儿”（Manchester Baby）是世界上第一台能运行的存储程序式电子计算机。虽然没有执行实际计算任务，但它证明了存储程序概念的可行性。",
      "category": "technology",
      "image": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1920&q=80",
      "theme": {
        "gradient": "linear-gradient(135deg, #1e212b 0%, #3a3f4b 100%)",
        "textColor": "light"
      }
    },
    {
      "id": "international-yoga-day-2014",
      "date": "06-21",
      "year": 2014,
      "title": "国际瑜伽日",
      "description": "2014 年联合国设立国际瑜伽日，旨在提高全世界对瑜伽益处的认识，促进身心健康的全球实践。",
      "category": "holiday",
      "image": "https://images.unsplash.com/photo-1544367563-12123d8965cd?w=1920&q=80",
      "theme": {
        "gradient": "linear-gradient(135deg, #1a3a2a 0%, #2d5a45 100%)",
        "textColor": "light"
      }
    },
    {
      "id": "greenland-self-rule-2009",
      "date": "06-21",
      "year": 2009,
      "title": "格陵兰岛实现自治",
      "description": "2009 年 6 月 21 日，格陵兰岛通过公投获得更大自治权，控制 police、法院和海岸警卫队，丹麦保留外交与防务权力。",
      "category": "politics",
      "image": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=1920&q=80",
      "theme": {
        "gradient": "linear-gradient(135deg, #0f2e3a 0%, #1a4a5c 100%)",
        "textColor": "light"
      }
    },
    {
      "id": "rocky-mountains-national-park-1915",
      "date": "06-21",
      "year": 1915,
      "title": "落基山国家公园成立",
      "description": "美国总统伍德罗·威尔逊签署法案，正式建立落基山国家公园，保护科罗拉多州壮丽的山脉、森林和野生动物。",
      "category": "culture",
      "image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1920&q=80",
      "theme": {
        "gradient": "linear-gradient(135deg, #2d3a3a 0%, #4a5e5e 100%)",
        "textColor": "light"
      }
    }
  ]
}
```

- [ ] **Step 2: 验证 JSON 格式**

Run: `python3 -m json.tool /workspace/data/events.json > /dev/null && echo "valid"`
Expected: `valid`

---

### Task 3: 实现数据层

**Files:**
- Modify: `/workspace/js/data.js`

- [ ] **Step 1: 实现日期解析和事件查询函数**

```javascript
// js/data.js
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
```

- [ ] **Step 2: 手动测试数据函数**

在 `index.html` 中临时添加测试脚本：

```html
<script type="module">
  import { getEventsForDate, formatDisplayDate } from './js/data.js';
  const events = await getEventsForDate(new Date(2026, 5, 21));
  console.log(events.length, events[0]?.title);
  console.log(formatDisplayDate(new Date(2026, 5, 21)));
</script>
```

Run: 用浏览器打开 `index.html` 并查看控制台
Expected: 控制台输出 `4` 和 `“小婴儿”计算机首次成功运行` 以及 `2026 年 6 月 21 日`

---

### Task 4: 渲染事件区块

**Files:**
- Modify: `/workspace/js/renderer.js`

- [ ] **Step 1: 实现事件 DOM 生成**

```javascript
// js/renderer.js
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

function renderEvents(events, container) {
  container.innerHTML = '';
  const total = events.length;
  events.forEach((event, index) => {
    const section = createEventSection(event, index, total);
    container.appendChild(section);
  });
}

export { renderEvents };
```

- [ ] **Step 2: 验证渲染输出**

在 `index.html` 中临时添加：

```html
<main id="app"></main>
<script type="module">
  import { getEventsForDate } from './js/data.js';
  import { renderEvents } from './js/renderer.js';
  const events = await getEventsForDate(new Date(2026, 5, 21));
  renderEvents(events, document.getElementById('app'));
</script>
```

Run: 用浏览器打开 `index.html`
Expected: 页面出现 4 个全屏事件区块，每个包含背景图、标题、描述、年份水印和进度文字

---

### Task 5: 基础样式（全局 + 事件区块 + 滚动吸附）

**Files:**
- Modify: `/workspace/css/style.css`

- [ ] **Step 1: 写入基础样式**

```css
/* css/style.css */
*, *::before, *::after {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
  overflow: hidden;
  background: #0f0f11;
  color: #fff;
}

#app {
  height: 100vh;
  overflow-y: scroll;
  scroll-snap-type: y mandatory;
  scroll-behavior: smooth;
}

.event-section {
  position: relative;
  width: 100%;
  height: 100vh;
  flex-shrink: 0;
  scroll-snap-align: start;
  scroll-snap-stop: always;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 28px;
  background: var(--event-gradient);
}

.event-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  transform: scale(1.1);
  transition: transform 0.1s linear;
  z-index: 0;
}

.event-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.25) 100%);
  z-index: 1;
}

.event-content {
  position: relative;
  z-index: 2;
  max-width: 75%;
  margin-top: auto;
  margin-bottom: auto;
}

.event-meta {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  opacity: 0.65;
  margin-bottom: 10px;
}

.event-title {
  font-size: clamp(28px, 5vw, 56px);
  line-height: 1.05;
  font-weight: 800;
  margin: 0 0 16px 0;
}

.event-description {
  font-size: clamp(14px, 1.6vw, 18px);
  line-height: 1.75;
  opacity: 0.9;
  margin: 0;
  max-width: 520px;
}

.event-year-watermark {
  position: absolute;
  left: 28px;
  bottom: 28px;
  font-size: clamp(48px, 10vw, 120px);
  font-weight: 900;
  opacity: 0.08;
  line-height: 1;
  z-index: 1;
  pointer-events: none;
}

.event-progress {
  position: absolute;
  right: 28px;
  bottom: 28px;
  font-size: 12px;
  opacity: 0.55;
  z-index: 2;
}

.text-dark .event-title,
.text-dark .event-description,
.text-dark .event-meta,
.text-dark .event-progress {
  color: #111;
}

.text-dark .event-overlay {
  background: linear-gradient(135deg, rgba(255,255,255,0.45) 0%, rgba(255,255,255,0.15) 100%);
}

@media (max-width: 768px) {
  .event-section {
    padding: 20px;
  }
  .event-content {
    max-width: 90%;
  }
  .event-year-watermark {
    left: 20px;
    bottom: 20px;
  }
  .event-progress {
    right: 20px;
    bottom: 20px;
  }
}
```

- [ ] **Step 2: 验证滚动吸附**

Run: 用浏览器打开 `index.html`，上下滚动鼠标
Expected: 每次滚动自然停在一个事件的最顶部，不会卡在两个事件之间

---

### Task 6: 顶部日期导航

**Files:**
- Modify: `/workspace/index.html`
- Modify: `/workspace/css/style.css`
- Modify: `/workspace/js/app.js`

- [ ] **Step 1: 在 index.html 中添加导航 HTML**

```html
<nav class="date-nav">
  <div class="brand">On This Day</div>
  <div class="date-controls">
    <button id="prev-date" aria-label="前一天">‹</button>
    <span id="current-date">2026 年 6 月 21 日</span>
    <button id="next-date" aria-label="后一天">›</button>
  </div>
</nav>
<main id="app"></main>
```

- [ ] **Step 2: 添加导航样式**

```css
.date-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 28px;
  z-index: 100;
  color: #fff;
  pointer-events: none;
}

.date-nav > * {
  pointer-events: auto;
}

.brand {
  font-weight: 700;
  font-size: 16px;
  letter-spacing: 0.02em;
}

.date-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  padding: 6px 12px;
  border-radius: 8px;
}

.date-controls button {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  line-height: 1;
}

.date-controls span {
  font-size: 14px;
  font-weight: 600;
  min-width: 140px;
  text-align: center;
}

@media (max-width: 768px) {
  .date-nav {
    padding: 14px 20px;
  }
  .date-controls span {
    font-size: 13px;
    min-width: 110px;
  }
}
```

- [ ] **Step 3: 在 app.js 中实现日期切换逻辑**

```javascript
// js/app.js
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
}

prevBtn.addEventListener('click', () => loadDate(addDays(currentDate, -1)));
nextBtn.addEventListener('click', () => loadDate(addDays(currentDate, 1)));

loadDate(currentDate);

function initScrollAnimations() {
  // Placeholder for Task 7
}

export { loadDate };
```

- [ ] **Step 4: 验证日期切换**

Run: 用浏览器打开 `index.html`，点击 ‹ 和 › 按钮
Expected: 日期变化，页面重新渲染对应日期的事件；因为当前只有 06-21 数据，其他日期显示空白或提示

---

### Task 7: GSAP 滚动动画

**Files:**
- Modify: `/workspace/index.html`
- Modify: `/workspace/js/app.js`

- [ ] **Step 1: 在 index.html 中引入 GSAP 和 ScrollTrigger**

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
```

- [ ] **Step 2: 实现滚动入场和出场动画**

```javascript
// js/app.js
function initScrollAnimations() {
  gsap.registerPlugin(ScrollTrigger);
  ScrollTrigger.getAll().forEach(t => t.kill());

  const sections = document.querySelectorAll('.event-section');

  sections.forEach((section) => {
    const bg = section.querySelector('.event-bg');
    const title = section.querySelector('.event-title');
    const desc = section.querySelector('.event-description');
    const meta = section.querySelector('.event-meta');
    const watermark = section.querySelector('.event-year-watermark');

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: section,
        scroller: '#app',
        start: 'top bottom',
        end: 'bottom top',
        scrub: 0.5,
      }
    });

    tl.fromTo(bg, { scale: 1.15 }, { scale: 1.0, ease: 'none' }, 0);
    tl.fromTo(title, { y: 60, opacity: 0 }, { y: 0, opacity: 1, ease: 'none' }, 0.1);
    tl.fromTo(desc, { y: 40, opacity: 0 }, { y: 0, opacity: 1, ease: 'none' }, 0.2);
    tl.fromTo(meta, { y: 20, opacity: 0 }, { y: 0, opacity: 1, ease: 'none' }, 0.05);
    tl.fromTo(watermark, { y: 80, opacity: 0 }, { y: 0, opacity: 0.08, ease: 'none' }, 0);

    const exitTl = gsap.timeline({
      scrollTrigger: {
        trigger: section,
        scroller: '#app',
        start: 'center center',
        end: 'bottom top',
        scrub: 0.5,
      }
    });

    exitTl.to([title, desc, meta], { y: -60, opacity: 0, ease: 'none' }, 0);
    exitTl.to(bg, { filter: 'blur(4px)', ease: 'none' }, 0);
  });
}
```

- [ ] **Step 3: 验证动画效果**

Run: 用浏览器打开 `index.html`，上下滚动
Expected: 事件进入时标题和描述从下方淡入，背景图从放大缩放到正常；事件退出时文字向上淡出，背景轻微模糊

---

### Task 8: 鼠标视差交互

**Files:**
- Modify: `/workspace/js/app.js`

- [ ] **Step 1: 实现鼠标移动视差**

```javascript
// 在 app.js 中添加
function initMouseParallax() {
  document.addEventListener('mousemove', (e) => {
    const x = (e.clientX / window.innerWidth - 0.5) * 2;
    const y = (e.clientY / window.innerHeight - 0.5) * 2;

    const activeBg = document.querySelector('.event-section.active .event-bg');
    if (!activeBg) return;

    gsap.to(activeBg, {
      x: -x * 15,
      y: -y * 15,
      duration: 0.6,
      ease: 'power2.out'
    });
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

app.addEventListener('scroll', () => {
  requestAnimationFrame(updateActiveSection);
});

initMouseParallax();
```

- [ ] **Step 2: 验证鼠标视差**

Run: 用浏览器打开 `index.html`，移动鼠标
Expected: 当前可见事件的背景图轻微跟随鼠标反向移动

---

### Task 9: 键盘导航

**Files:**
- Modify: `/workspace/js/app.js`

- [ ] **Step 1: 实现键盘上下切换**

```javascript
// 在 app.js 中添加
app.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowDown' || e.key === 'PageDown') {
    e.preventDefault();
    scrollToNextSection();
  } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
    e.preventDefault();
    scrollToPrevSection();
  }
});

function scrollToNextSection() {
  const current = app.scrollTop;
  const sectionHeight = window.innerHeight;
  const nextIndex = Math.round(current / sectionHeight) + 1;
  app.scrollTo({ top: nextIndex * sectionHeight, behavior: 'smooth' });
}

function scrollToPrevSection() {
  const current = app.scrollTop;
  const sectionHeight = window.innerHeight;
  const prevIndex = Math.round(current / sectionHeight) - 1;
  app.scrollTo({ top: Math.max(0, prevIndex * sectionHeight), behavior: 'smooth' });
}
```

- [ ] **Step 2: 验证键盘导航**

Run: 用浏览器打开 `index.html`，按键盘 ↑/↓ 键
Expected: 页面平滑滚动到上/下一个事件

---

### Task 10: 空状态与多日期数据

**Files:**
- Modify: `/workspace/js/renderer.js`
- Modify: `/workspace/data/events.json`

- [ ] **Step 1: 添加空状态渲染**

```javascript
// 在 renderer.js 中添加
function renderEmptyState(container, date) {
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

function renderEvents(events, container, date) {
  container.innerHTML = '';
  if (events.length === 0) {
    renderEmptyState(container, date);
    return;
  }
  const total = events.length;
  events.forEach((event, index) => {
    const section = createEventSection(event, index, total);
    container.appendChild(section);
  });
}
```

- [ ] **Step 2: 为 6 月 22 日添加一个事件**

在 `events.json` 的 `events` 数组中添加：

```json
{
  "id": "gagarin-spaceflight-1941",
  "date": "06-22",
  "year": 1941,
  "title": "德国入侵苏联（巴巴罗萨行动）",
  "description": "1941 年 6 月 22 日，纳粹德国发动巴巴罗萨行动，撕毁《苏德互不侵犯条约》，对苏联发动突然袭击。",
  "category": "politics",
  "image": "https://images.unsplash.com/photo-1598892861701-7f178527a52e?w=1920&q=80",
  "theme": {
    "gradient": "linear-gradient(135deg, #2d1b2e 0%, #4a2f4d 100%)",
    "textColor": "light"
  }
}
```

- [ ] **Step 3: 验证空状态和多日期**

Run: 用浏览器打开 `index.html`
Expected:
- 6 月 21 日显示 4 个事件
- 切换到 6 月 22 日显示 1 个事件
- 切换到 6 月 23 日显示空状态提示

---

### Task 11: 最终整合与验证

**Files:**
- Modify: `/workspace/index.html`

- [ ] **Step 1: 完善 index.html 最终结构**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>On This Day - 历史上的今天</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=Noto+Sans+SC:wght@400;600;700;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="./css/style.css">
</head>
<body>
  <nav class="date-nav">
    <div class="brand">On This Day</div>
    <div class="date-controls">
      <button id="prev-date" aria-label="前一天">‹</button>
      <span id="current-date">Loading...</span>
      <button id="next-date" aria-label="后一天">›</button>
    </div>
  </nav>

  <main id="app" tabindex="0" aria-label="事件列表"></main>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
  <script type="module" src="./js/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: 最终浏览器验证**

Run: 用浏览器打开 `index.html`，执行以下操作：
1. 上下滚动切换事件，确认吸附正常
2. 点击日期 ‹ › 切换日期
3. 移动鼠标观察背景视差
4. 按 ↑/↓ 键切换事件
5. 切换到无数据日期查看空状态

Expected: 所有交互正常，动画流畅，无 JavaScript 报错

---

## Spec Coverage Check

| Spec 要求 | 对应任务 |
|-----------|----------|
| 每个事件占满 100vh | Task 5 |
| 上下滚动切换 + 吸附 | Task 5 |
| 华丽动画（视差、缩放、淡入淡出） | Task 7 |
| 鼠标动作识别 | Task 8 |
| 日期导航 | Task 6 |
| 事件进度指示 | Task 4 |
| 本地静态数据源 | Task 2, Task 3 |
| 氛围随节日主题变化 | Task 2, Task 4 |
| 键盘可访问 | Task 9 |
| 响应式 | Task 5 |

## Placeholder Scan

- 无 TBD/TODO
- 无 "implement later"
- 无未定义的函数引用
- 所有代码块完整

## Type Consistency

- `getEventsForDate(date)` 接收 `Date` 对象
- `renderEvents(events, container, date)` 接收事件数组、DOM 容器、Date 对象
- `loadDate(date)` 接收 `Date` 对象
- 所有日期格式化使用 `formatDate` / `formatDisplayDate` / `addDays`
