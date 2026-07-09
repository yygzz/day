import feedparser
import json
import os
import time
from datetime import datetime, timedelta
from hashlib import md5

RSS_FEEDS = [
    {"name": "NPR", "url": "https://www.npr.org/rss/rss.php?id=1001"},
    {"name": "ABC News", "url": "https://abcnews.go.com/abcnews/internationalheadlines"},
    {"name": "CBS News", "url": "https://www.cbsnews.com/latest/rss/world"},
    {"name": "China Daily", "url": "https://www.chinadaily.com.cn/rss/world_rss.xml"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Reuters", "url": "http://feeds.reuters.com/reuters/worldNews"},
    {"name": "CNN", "url": "http://rss.cnn.com/rss/edition_world.rss"},
    {"name": "New York Times", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
]

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "news.json")
TARGET_COUNT = 20

def fetch_rss_feed(url, source_name):
    try:
        feed = feedparser.parse(url)
        
        news_items = []
        today = datetime.now().date()
        
        for entry in feed.entries:
            try:
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6]).date()
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6]).date()
                
                if pub_date and pub_date < today - timedelta(days=2):
                    continue
                
                title = getattr(entry, 'title', '').strip()
                link = getattr(entry, 'link', '').strip()
                summary = getattr(entry, 'summary', '').strip()[:500]
                
                if not title or not link:
                    continue
                
                news_items.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "source": source_name,
                    "pub_date": pub_date.strftime("%Y-%m-%d") if pub_date else "",
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception:
                continue
        
        return news_items
    except Exception:
        return []

def deduplicate(news_list):
    seen = set()
    unique = []
    for item in news_list:
        key = md5((item['title'] + item['link']).encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique

def main():
    all_news = []
    
    for feed in RSS_FEEDS:
        items = fetch_rss_feed(feed['url'], feed['name'])
        all_news.extend(items)
        time.sleep(1)
    
    all_news = deduplicate(all_news)
    all_news.sort(key=lambda x: x['pub_date'] or '', reverse=True)
    
    if len(all_news) > TARGET_COUNT:
        all_news = all_news[:TARGET_COUNT]
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_news, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

if __name__ == "__main__":
    main()