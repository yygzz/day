import os
import json
import feedparser
from datetime import datetime, timedelta
from hashlib import md5

RSS_FEEDS = [
    "https://feeds.npr.org/1001/rss.xml",
    "https://abcnews.go.com/abcnews/internationalheadlines",
    "https://www.cbsnews.com/latest/rss/world",
    "https://www.chinadaily.com.cn/rss/world_rss.xml",
    "https://www.reutersagency.com/feed/?best-topics=world&post-type=best",
    "https://www.bbc.co.uk/news/rss.xml",
    "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/world/rss.xml",
    "https://www.washingtonpost.com/rss/world",
]

def get_hash(text):
    return md5(text.encode('utf-8')).hexdigest()

def fetch_rss_feed(url):
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries:
            title = getattr(entry, 'title', '').strip()
            link = getattr(entry, 'link', '').strip()
            published = getattr(entry, 'published', '')
            summary = getattr(entry, 'summary', getattr(entry, 'description', '')).strip()
            
            if not title or not link:
                continue
            
            try:
                if published:
                    published_time = feedparser.parse_date(published)
                else:
                    published_time = datetime.now()
            except:
                published_time = datetime.now()
            
            articles.append({
                'title': title,
                'link': link,
                'published': published_time.isoformat(),
                'summary': summary[:500] if summary else '',
                'source': url.split('/')[2],
            })
        return articles
    except Exception:
        return []

def is_recent(published_time_str):
    try:
        published_time = datetime.fromisoformat(published_time_str.replace('Z', '+00:00'))
        today = datetime.now()
        return (today - published_time).days <= 30
    except:
        return True

def main():
    all_articles = []
    seen_hashes = set()
    
    for url in RSS_FEEDS:
        articles = fetch_rss_feed(url)
        for article in articles:
            article_hash = get_hash(article['title'] + article['link'])
            if article_hash not in seen_hashes and is_recent(article['published']):
                seen_hashes.add(article_hash)
                all_articles.append(article)
    
    all_articles.sort(key=lambda x: x['published'], reverse=True)
    
    output = {
        'updated_at': datetime.now().isoformat(),
        'count': len(all_articles),
        'articles': all_articles
    }
    
    os.makedirs('/workspace/data', exist_ok=True)
    with open('/workspace/data/news.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()