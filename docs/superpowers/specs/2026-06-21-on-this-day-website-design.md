# On This Day 网站设计文档

## 项目背景

一个每天展示 3-5 个对国际具有重要意义的日子（历史事件、国际节日、纪念日等）的网站。每个日子包含图片、标题、日期、描述，要求视觉冲击力强烈。

## 用户确认的设计方向

- **布局：** 每个事件严格占满整个网页视口（100vh），无分隔条，每天 3-5 个事件纵向堆叠。
- **交互：** 用户通过上下滚动鼠标滚轮 / 触摸滑动切换事件，滚动停止后自动吸附到完整的一屏。
- **视觉：** 氛围随节日主题变化（科技、自然、纪念日等使用不同的主色/背景风格）。
- **动画：** 华丽过渡，包括视差滚动、文字入场、背景缩放、鼠标位置影响背景偏移。
- **数据：** 混合模式，优先本地静态核心数据，架构预留 API 扩展接口。
- **导航：** 顶部固定日期导航，支持前后切换日期；显示事件进度（事件 N / M）。

## Visual Thesis

一本可以上下翻阅的“国际纪念日画报”：每一页都是一张全屏海报，日期是坐标，事件是主角，鼠标移动和滚动速度让画面产生呼吸感。

## Content Plan

1. **Hero / 焦点事件：** 每个事件占满 100vh，背景图/渐变全屏铺满，叠加标题、日期、描述、分类标签、年份水印。
2. **日期导航：** 顶部固定栏，品牌名 + 日期切换（前一天 / 当前日期 / 后一天）。
3. **事件指示器：** 底部或左侧显示当前事件索引，提示可继续滚动。
4. **详情状态（可选）：** 点击事件可展开更详细描述或相关链接（本阶段不实现，架构预留）。

## Interaction Thesis

1. **滚动吸附（Snap Scroll）：** 用户自由滚动，停止后平滑吸附到最近的事件中心。
2. **视差入场：** 事件进入视口时，背景图从 1.1 缩放到 1.0，标题从下方滑入淡入。
3. **鼠标视差：** 鼠标位置驱动背景/装饰层轻微反向偏移，增加沉浸感。

## 信息架构

```
On This Day Website
├── 首页（/）
│   └── 默认展示当天日期的事件
├── 日期页（/?date=YYYY-MM-DD 或 /YYYY-MM-DD）
│   └── 展示指定日期的事件
└── 数据源
    ├── 本地 JSON 事件库（核心）
    └── API 扩展接口（预留）
```

## 数据结构

```typescript
interface HistoricalEvent {
  id: string;
  date: string; // MM-DD
  year: number;
  title: string;
  description: string;
  category: 'technology' | 'science' | 'culture' | 'holiday' | 'society' | 'sports' | 'politics';
  image: string; // 图片 URL 或本地路径
  theme: {
    primaryColor: string;
    gradient: string;
    textColor: 'light' | 'dark';
  };
  source?: string; // 可选来源链接
}

interface DayData {
  date: string; // YYYY-MM-DD
  events: HistoricalEvent[];
}
```

## 组件清单

- `App`：应用根组件，管理当前日期和事件数据。
- `DateNavigator`：顶部日期导航栏。
- `EventSection`：单个事件的全屏展示区块。
- `EventIndicator`：事件进度指示器。
- `EventStore` / 数据层：读取本地 JSON，按日期返回事件列表，预留 API 扩展。

## 技术栈

- **框架：** 纯 HTML + CSS + JavaScript（或 React/Vite，视实现计划而定）。
- **动画：** GSAP + ScrollTrigger（推荐）或原生 CSS scroll-snap + Intersection Observer。
- **平滑滚动：** Lenis（可选，用于更顺滑的滚轮体验）。
- **数据源：** 本地 `events.json`，按 `MM-DD` 索引。

## 视觉规范

- **字体：** 一个无衬线字体用于标题和正文（如 Inter / Noto Sans SC）。
- **标题：** 大而粗，左对齐，最大宽度 75%。
- **正文：** 短句，15-16px，最大宽度 420-480px。
- **年份水印：** 极大字号（72px+），低透明度（0.08），置于左下角或背景中。
- **分类标签：** 小写大写字母，字间距宽，置于标题上方。
- **背景：** 全屏图片 + 深色渐变遮罩，或纯色渐变。根据事件主题变化。

## 主题色示例

| 分类 | 主色 | 背景风格 |
|------|------|----------|
| technology | 冷蓝灰 #1e212b → #3a3f4b | 科技插画/电路纹理 |
| science | 深青 #0f2e3a → #1a4a5c | 星空/实验室 |
| culture | 暖金 #3d2b1f → #5e4b35 | 艺术/历史场景 |
| holiday | 鲜绿 #1a3a2a → #2d5a45 | 自然/庆祝 |
| society | 深红紫 #2d1b2e → #4a2f4d | 社会运动 |

## 响应式

- **桌面：** 文字左对齐，年份水印在左下角，日期导航在顶部。
- **平板/手机：** 标题字号缩小，正文宽度 90%，日期导航简化，触摸滑动优先。

## 非功能需求

- 首屏加载时间 < 2s（本地数据 + 优化图片）。
- 动画在 60fps 下流畅运行。
- 键盘可访问：↑/↓、PageUp/PageDown 切换事件。
- 不需要后端，静态部署即可。

## 后续扩展（不在本期）

- 接入 Wikipedia / 日历 API 补充事件。
- 事件详情页/弹窗。
- 用户收藏/分享。
- 多语言支持。

## 参考

- 用户提供的示例图：CSDN 风格深色工业/科技插画 + 文字叠加。
- 视觉伴侣设计稿：`/workspace/.superpowers/brainstorm/2280-1782024981/content/design-detail-v5.html`
