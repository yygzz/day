#!/usr/bin/env python3
import json
import os
import hashlib
from datetime import datetime, timezone

import feedparser
import requests

RSS_FEEDS = [
    {
        "name": "NPR",
        "url": "https://feeds.npr.org/1004/rss.xml",
        "category": "World",
    },
    {
        "name": "NPR Top Stories",
        "url": "https://feeds.npr.org/1001/rss.xml",
        "category": "Top Stories",
    },
    {
        "name": "ABC News",
        "url": "https://abcnews.go.com/abcnews/internationalheadlines",
        "category": "World",
    },
    {
        "name": "ABC News Top",
        "url": "https://abcnews.go.com/abcnews/topstories",
        "category": "Top Stories",
    },
    {
        "name": "CBS News World",
        "url": "https://www.cbsnews.com/latest/rss/world",
        "category": "World",
    },
    {
        "name": "CBS News Top",
        "url": "https://www.cbsnews.com/latest/rss/main",
        "category": "Top Stories",
    },
    {
        "name": "China Daily World",
        "url": "https://www.chinadaily.com.cn/rss/world_rss.xml",
        "category": "World",
    },
    {
        "name": "China Daily China",
        "url": "https://www.chinadaily.com.cn/rss/china_rss.xml",
        "category": "China",
    },
]

MIN_NEWS_COUNT = 20
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "news.json")
USER_AGENT = "Mozilla/5.0 (compatible; NewsScraper/1.0)"


def fetch_feed(feed_info):
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(feed_info["url"], headers=headers, timeout=15)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        if feed.bozo and not feed.entries:
            return []
        return feed.entries
    except Exception:
        return []


def parse_entry(entry, feed_info):
    title = entry.get("title", "").strip()
    link = entry.get("link", "").strip()
    summary = entry.get("summary", "") or entry.get("description", "")
    summary = summary.strip()

    published = entry.get("published", "") or entry.get("updated", "")
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            published = dt.isoformat()
        except Exception:
            pass
    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            published = dt.isoformat()
        except Exception:
            pass

    if not title or not link:
        return None

    return {
        "title": title,
        "link": link,
        "summary": summary,
        "source": feed_info["name"],
        "category": feed_info["category"],
        "published": published,
    }


def deduplicate(news_items):
    seen = set()
    unique = []
    for item in news_items:
        key = hashlib.md5(item["title"].lower().encode("utf-8")).hexdigest()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def load_existing():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("news", [])
        except Exception:
            return []
    return []


def save_news(news_items):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(news_items),
        "news": news_items,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    all_news = []

    for feed_info in RSS_FEEDS:
        entries = fetch_feed(feed_info)
        for entry in entries:
            parsed = parse_entry(entry, feed_info)
            if parsed:
                all_news.append(parsed)

    all_news = deduplicate(all_news)

    existing = load_existing()

    if len(all_news) < MIN_NEWS_COUNT and existing:
        combined = all_news + existing
        combined = deduplicate(combined)
        if len(combined) > len(all_news):
            all_news = combined[: max(MIN_NEWS_COUNT, len(all_news))]

    if not all_news and existing:
        all_news = existing

    save_news(all_news)


if __name__ == "__main__":
    main()
