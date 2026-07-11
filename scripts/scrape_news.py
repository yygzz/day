#!/usr/bin/env python3
import feedparser
import json
import os
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse

RSS_FEEDS = [
    {"name": "NPR", "url": "https://feeds.npr.org/1004/rss.xml", "category": "World"},
    {"name": "NPR", "url": "https://feeds.npr.org/1001/rss.xml", "category": "News"},
    {"name": "ABC News", "url": "https://abcnews.go.com/abcnews/internationalheadlines", "category": "World"},
    {"name": "ABC News", "url": "https://abcnews.go.com/abcnews/topstories", "category": "Top Stories"},
    {"name": "CBS News", "url": "https://www.cbsnews.com/latest/rss/world", "category": "World"},
    {"name": "CBS News", "url": "https://www.cbsnews.com/latest/rss/politics", "category": "Politics"},
    {"name": "China Daily", "url": "https://www.chinadaily.com.cn/rss/world_rss.xml", "category": "World"},
    {"name": "China Daily", "url": "https://www.chinadaily.com.cn/rss/china_rss.xml", "category": "China"},
    {"name": "Reuters", "url": "https://www.reutersagency.com/feed/?best-topics=world&post_type=best", "category": "World"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "category": "World"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/technology/rss.xml", "category": "Technology"},
    {"name": "CNN", "url": "http://rss.cnn.com/rss/edition_world.rss", "category": "World"},
    {"name": "CNN", "url": "http://rss.cnn.com/rss/edition.rss", "category": "Top Stories"},
]

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "news.json")
MIN_NEWS = 20


def get_news_id(title, url):
    return hashlib.md5(f"{title.strip().lower()}|{url.strip().lower()}".encode()).hexdigest()


def parse_date(entry):
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def get_summary(entry):
    if hasattr(entry, "summary") and entry.summary:
        return entry.summary
    if hasattr(entry, "description") and entry.description:
        return entry.description
    return ""


def clean_html(text):
    import re
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def scrape_feed(feed_info):
    news_items = []
    try:
        feed = feedparser.parse(feed_info["url"])
        if feed.bozo and not feed.entries:
            return news_items
        for entry in feed.entries:
            if not hasattr(entry, "title") or not entry.title:
                continue
            title = clean_html(entry.title)
            url = entry.link if hasattr(entry, "link") else ""
            if not url:
                continue
            summary = clean_html(get_summary(entry))
            published = parse_date(entry)
            news_items.append({
                "id": get_news_id(title, url),
                "title": title,
                "url": url,
                "source": feed_info["name"],
                "category": feed_info["category"],
                "summary": summary[:300],
                "published_at": published,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })
    except Exception:
        pass
    return news_items


def load_existing_news():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                if isinstance(data, dict) and "news" in data:
                    return data["news"]
        except Exception:
            pass
    return []


def save_news(news_list):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(news_list),
        "news": news_list,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


def main():
    existing_news = load_existing_news()
    seen_ids = {item["id"] for item in existing_news} if isinstance(existing_news, list) else set()

    all_news = list(existing_news) if isinstance(existing_news, list) else []

    for feed_info in RSS_FEEDS:
        items = scrape_feed(feed_info)
        for item in items:
            if item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                all_news.append(item)

    all_news.sort(key=lambda x: x.get("published_at", ""), reverse=True)

    if len(all_news) < MIN_NEWS:
        save_news(all_news)
        return

    save_news(all_news)


if __name__ == "__main__":
    main()
