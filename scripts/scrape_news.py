import requests
import feedparser
import json
import os
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
from hashlib import md5

RSS_SOURCES = [
    {"name": "NPR", "url": "https://feeds.npr.org/1001/rss.xml"},
    {"name": "ABC News", "url": "https://abcnews.go.com/abcnews/topstories"},
    {"name": "ABC News RSS", "url": "https://feeds.abcnews.com/abcnews/topstories"},
    {"name": "CBS News", "url": "https://www.cbsnews.com/latest/rss/main"},
    {"name": "China Daily", "url": "https://www.chinadaily.com.cn/rss/world_rss.xml"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Reuters", "url": "http://feeds.reuters.com/Reuters/worldNews"},
    {"name": "The New York Times", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"name": "CNN", "url": "http://rss.cnn.com/rss/cnn_world.rss"},
]

TARGET_COUNT = 20
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "news.json")

def fetch_rss_feed(url, timeout=10):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return feedparser.parse(response.content)
    except Exception:
        return None

def is_recent(entry):
    try:
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            entry_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            entry_time = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        else:
            return True
        
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=48)
        
        return entry_time >= cutoff_time
    except Exception:
        return True

def get_entry_id(entry):
    if hasattr(entry, 'link') and entry.link:
        return entry.link
    if hasattr(entry, 'title') and entry.title:
        return md5(entry.title.encode()).hexdigest()
    return None

def parse_rss_entries(feed, source_name):
    entries = []
    if not feed or not hasattr(feed, 'entries'):
        return entries
    
    for entry in feed.entries:
        if not is_recent(entry):
            continue
        
        entry_id = get_entry_id(entry)
        if not entry_id:
            continue
        
        title = getattr(entry, 'title', '')
        link = getattr(entry, 'link', '')
        summary = getattr(entry, 'summary', '')
        published = getattr(entry, 'published', '')
        
        entries.append({
            "id": entry_id,
            "title": title[:200] if title else '',
            "link": link[:500] if link else '',
            "summary": summary[:500] if summary else '',
            "source": source_name,
            "published": published,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    return entries

def scrape_news():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    all_entries = []
    seen_ids = set()
    
    for source in RSS_SOURCES:
        feed = fetch_rss_feed(source["url"])
        if not feed:
            continue
        
        entries = parse_rss_entries(feed, source["name"])
        for entry in entries:
            if entry["id"] not in seen_ids:
                seen_ids.add(entry["id"])
                all_entries.append(entry)
    
    all_entries.sort(key=lambda x: x.get("published", ""), reverse=True)
    
    result = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(all_entries),
        "news": all_entries
    }
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_news()