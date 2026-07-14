import json
import os
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
import feedparser


RSS_FEEDS = [
    {"name": "NPR World", "url": "https://feeds.npr.org/1003/rss.xml"},
    {"name": "ABC News World", "url": "https://abcnews.go.com/abcnews/internationalheadlines"},
    {"name": "CBS News World", "url": "https://www.cbsnews.com/latest/rss/world"},
    {"name": "China Daily World", "url": "https://www.chinadaily.com.cn/rss/world_rss.xml"},
    {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Reuters World", "url": "http://feeds.reuters.com/Reuters/worldNews"},
    {"name": "CNN World", "url": "http://rss.cnn.com/rss/edition_world.rss"},
    {"name": "Guardian World", "url": "https://www.theguardian.com/world/rss"},
]


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_datetime(date_str: str) -> Optional[str]:
    formats = [
        '%a, %d %b %Y %H:%M:%S %Z',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%SZ',
        '%a, %d %b %Y %H:%M:%S',
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue
    return datetime.now().isoformat()


def fetch_rss_feed(feed_info: Dict[str, str]) -> List[Dict[str, Any]]:
    articles = []
    try:
        response = requests.get(feed_info['url'], timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        
        for entry in feed.entries:
            title = clean_text(entry.get('title', ''))
            link = entry.get('link', '')
            summary = clean_text(entry.get('summary', '') or entry.get('description', ''))
            published = entry.get('published', '') or entry.get('updated', '')
            
            if not title or not link:
                continue
            
            articles.append({
                'title': title,
                'link': link,
                'summary': summary[:500],
                'source': feed_info['name'],
                'published_at': parse_datetime(published),
                'scraped_at': datetime.now().isoformat(),
            })
    except Exception:
        pass
    return articles


def scrape_news(target_count: int = 20) -> List[Dict[str, Any]]:
    all_articles = []
    seen_titles = set()
    seen_links = set()

    for feed_info in RSS_FEEDS:
        articles = fetch_rss_feed(feed_info)
        for article in articles:
            title_lower = article['title'].lower()
            link_lower = article['link'].lower()
            
            if title_lower in seen_titles or link_lower in seen_links:
                continue
            
            seen_titles.add(title_lower)
            seen_links.add(link_lower)
            all_articles.append(article)
            
            if len(all_articles) >= target_count:
                break
        if len(all_articles) >= target_count:
            break

    return all_articles


def main():
    news = scrape_news(target_count=20)
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    news_file = os.path.join(data_dir, 'news.json')
    
    result = {
        'count': len(news),
        'scraped_at': datetime.now().isoformat(),
        'articles': news,
    }
    
    with open(news_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()