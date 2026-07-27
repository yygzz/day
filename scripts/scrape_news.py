import os
import json
import feedparser
from datetime import datetime, timedelta
from urllib.parse import urlparse
import hashlib

RSS_FEEDS = [
    "https://www.npr.org/rss/rss.php?id=1001",
    "https://abcnews.go.com/abcnews/topstories",
    "https://www.cbsnews.com/latest/rss/main",
    "https://www.chinadaily.com.cn/rss/china_rss.xml",
    "https://www.chinadaily.com.cn/rss/world_rss.xml",
    "https://www.bbc.co.uk/news/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.reutersagency.com/feed/?best-topics=world&post-type=best",
    "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/world/rss.xml",
    "https://feeds.feedburner.com/breakingnews",
]

def fetch_rss_feed(url):
    try:
        feed = feedparser.parse(url)
        return feed.entries if feed.entries else []
    except Exception:
        return []

def is_today(entry):
    try:
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            entry_date = datetime(*entry.published_parsed[:6])
            today = datetime.now()
            return (today - entry_date).days <= 1
        return True
    except Exception:
        return True

def extract_entry_data(entry):
    title = getattr(entry, 'title', '').strip()
    link = getattr(entry, 'link', '')
    published = getattr(entry, 'published', '')
    summary = ''
    if hasattr(entry, 'summary'):
        summary = entry.summary.strip()
    elif hasattr(entry, 'description'):
        summary = str(entry.description).strip()
    
    return {
        'title': title,
        'link': link,
        'published': published,
        'summary': summary[:500] if summary else '',
        'source': urlparse(link).hostname if link else 'unknown',
        'id': hashlib.md5(title.encode('utf-8')).hexdigest()[:16]
    }

def scrape_news():
    all_news = []
    seen_ids = set()
    
    for feed_url in RSS_FEEDS:
        entries = fetch_rss_feed(feed_url)
        for entry in entries:
            if not is_today(entry):
                continue
            data = extract_entry_data(entry)
            if data['id'] not in seen_ids and data['title']:
                seen_ids.add(data['id'])
                all_news.append(data)
    
    all_news.sort(key=lambda x: x['published'] or '', reverse=True)
    
    os.makedirs('data', exist_ok=True)
    with open('data/news.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    return len(all_news)

if __name__ == '__main__':
    scrape_news()