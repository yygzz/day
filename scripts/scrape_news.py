#!/usr/bin/env python3

import os
import json
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional

RSS_SOURCES = [
    {"name": "NPR", "url": "https://feeds.npr.org/1001/rss.xml"},
    {"name": "ABC News", "url": "https://abcnews.go.com/abcnews/internationalheadlines"},
    {"name": "CBS News", "url": "https://www.cbsnews.com/latest/rss/world"},
    {"name": "China Daily", "url": "https://www.chinadaily.com.cn/rss/world_rss.xml"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Reuters", "url": "https://www.reutersagency.com/feed/?best-topics=world&post-type=best"},
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
    {"name": "New York Times", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"name": "CNN", "url": "http://rss.cnn.com/rss/edition_world.rss"},
    {"name": "AP News", "url": "https://apnews.com/rss/world"},
]

TARGET_COUNT = 20
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
NEWS_FILE = os.path.join(DATA_DIR, "news.json")


def fetch_rss_feed(url: str) -> Optional[feedparser.FeedParserDict]:
    try:
        return feedparser.parse(url)
    except Exception:
        return None


def is_today(date_str: str) -> bool:
    try:
        if date_str:
            parsed_date = feedparser._parse_date(date_str)
            if parsed_date:
                today = datetime.now().date()
                return parsed_date.date() >= today - timedelta(days=1)
    except Exception:
        pass
    return True


def parse_entries(feed: feedparser.FeedParserDict, source_name: str) -> List[Dict]:
    entries = []
    for entry in feed.get("entries", []):
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        summary = entry.get("summary", "").strip()[:200]
        published = entry.get("published", "")
        
        if not title or not link:
            continue
        
        if not is_today(published):
            continue
        
        entries.append({
            "title": title,
            "link": link,
            "summary": summary,
            "source": source_name,
            "published": published,
            "timestamp": datetime.now().isoformat()
        })
    return entries


def remove_duplicates(news_list: List[Dict]) -> List[Dict]:
    seen = set()
    unique = []
    for item in news_list:
        key = item["title"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def save_news(news_list: List[Dict]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    
    existing = []
    if os.path.exists(NEWS_FILE):
        try:
            with open(NEWS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            pass
    
    all_news = news_list + existing
    all_news = remove_duplicates(all_news)
    all_news = all_news[:TARGET_COUNT]
    
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)


def main() -> None:
    all_entries = []
    
    for source in RSS_SOURCES:
        feed = fetch_rss_feed(source["url"])
        if feed:
            entries = parse_entries(feed, source["name"])
            all_entries.extend(entries)
    
    all_entries = remove_duplicates(all_entries)
    all_entries = sorted(all_entries, key=lambda x: x["published"] or "", reverse=True)
    
    save_news(all_entries)


if __name__ == "__main__":
    main()