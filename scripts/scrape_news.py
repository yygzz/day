import os
import json
import ssl
import hashlib
from datetime import datetime
from typing import List, Dict

import feedparser

ssl._create_default_https_context = ssl._create_unverified_context

RSS_SOURCES = [
    {"name": "NPR", "url": "https://feeds.npr.org/1001/rss.xml"},
    {"name": "CBS News", "url": "https://www.cbsnews.com/latest/rss/world"},
    {"name": "China Daily", "url": "https://www.chinadaily.com.cn/rss/world.xml"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "CNN", "url": "http://rss.cnn.com/rss/edition_world.rss"},
    {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "NPR World", "url": "https://feeds.npr.org/1004/rss.xml"},
    {"name": "AP News", "url": "https://rss.publico.es/rss/publico/politica.xml"},
]

TARGET_COUNT = 20
MAX_PER_SOURCE = 15


def get_hash(text: str) -> str:
    return hashlib.md5(text.strip().lower().encode()).hexdigest()


def parse_rss_feed(source: Dict[str, str]) -> List[Dict]:
    articles = []
    try:
        feed = feedparser.parse(source["url"])
        if feed.bozo != 0:
            return articles
        
        today = datetime.now().date()
        for entry in feed.entries[:MAX_PER_SOURCE]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            description = entry.get("description", "").strip()
            pub_date = entry.get("published", entry.get("updated", ""))
            
            if not title or not link:
                continue
            
            articles.append({
                "title": title,
                "link": link,
                "description": description,
                "source": source["name"],
                "published": pub_date,
                "hash": get_hash(title + link)
            })
    except Exception:
        pass
    return articles


def scrape_news() -> List[Dict]:
    all_articles = []
    seen_hashes = set()
    
    for source in RSS_SOURCES:
        articles = parse_rss_feed(source)
        for article in articles:
            if article["hash"] not in seen_hashes:
                seen_hashes.add(article["hash"])
                all_articles.append(article)
        
        if len(all_articles) >= TARGET_COUNT:
            break
    
    all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
    return all_articles[:TARGET_COUNT]


def save_news(articles: List[Dict], filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    data = {
        "articles": articles,
        "count": len(articles),
        "updated_at": datetime.now().isoformat(),
        "sources": [s["name"] for s in RSS_SOURCES]
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    news_data = scrape_news()
    save_news(news_data, "data/news.json")


if __name__ == "__main__":
    main()