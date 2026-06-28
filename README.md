# 历史上的今天 · 国际新闻

一个展示国际重大日子与实时新闻的全屏滚动网站。采用 Liquid Glass 设计语言，支持历史事件与新闻视图切换。

## 功能

- **历史上的今天**：按日期展示全年国际重大事件，含图片、年份、分类与描述
- **国际新闻**：纵向滚动展示本周国际新闻，含可靠性 / 重要性评分、评价、时间地点人物与原文链接
- **节日栏**：当前日期对应的国际节日展示
- **日期导航**：支持前后翻页、日历选择、回到今天
- **全屏滚动**：GSAP + ScrollTrigger 实现平滑滚动与吸附

## 技术栈

- HTML5 / CSS3（Liquid Glass、圆角、响应式）
- JavaScript ES6 Modules
- GSAP + ScrollTrigger
- Google Fonts（Inter / Noto Sans SC）

## 项目结构

```
/workspace
├── index.html              # 页面入口
├── css/style.css           # 全局样式
├── js/
│   ├── app.js              # 主逻辑、视图切换、滚动动画
│   ├── renderer.js         # 历史事件渲染
│   ├── newsRenderer.js     # 新闻渲染
│   └── data.js             # 数据读取与工具函数
├── data/
│   ├── events.json         # 全年历史事件
│   └── news.json           # 本周新闻数据
└── scripts/
    ├── scrape_full_year.py # 历史事件抓取脚本
    └── scrape_news.py      # 新闻抓取脚本
```

## 本地运行

使用任意静态服务器启动项目根目录，例如：

```bash
python -m http.server 8081
```

然后访问 `http://localhost:8081/`。

## 数据来源

- 历史事件：`https://allthatsinteresting.com/today-in-history/full-year`
- 新闻：CCTV、BBC、ABC、X（Twitter）、微博等权威渠道
