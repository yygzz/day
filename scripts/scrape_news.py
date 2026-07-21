import os
import json
import feedparser
from datetime import datetime, timedelta
from hashlib import md5

RSS_FEEDS = [
    ("NPR", "https://www.npr.org/rss/rss.php?id=1001"),
    ("ABC News", "https://abcnews.go.com/abcnews/internationalheadlines"),
    ("CBS News", "https://www.cbsnews.com/latest/rss/world"),
    ("China Daily", "https://www.chinadaily.com.cn/rss/world_rss.xml"),
    ("BBC News", "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ("Reuters", "https://www.reutersagency.com/feed/?best-topics=world&post-type=best"),
    ("CNN", "http://rss.cnn.com/rss/edition_world.rss"),
]

def fetch_rss_feed(url, source):
    try:
        feed = feedparser.parse(url)
        articles = []
        today = datetime.now().date()
        
        for entry in feed.entries:
            try:
                published = entry.get("published", "")
                if published:
                    try:
                        pub_date = feedparser.parse_date(published).date()
                        days_diff = (today - pub_date).days
                        if days_diff > 3:
                            continue
                    except:
                        pass
                
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                summary = entry.get("summary", "").strip()[:500]
                
                if not title or not link:
                    continue
                
                articles.append({
                    "source": source,
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "published": published,
                    "scraped_at": datetime.now().isoformat()
                })
            except Exception:
                continue
        
        return articles
    except Exception:
        return []

def deduplicate_articles(articles):
    seen = set()
    unique = []
    
    for article in articles:
        key = md5(article["title"].encode("utf-8")).hexdigest()
        if key not in seen:
            seen.add(key)
            unique.append(article)
    
    return unique

def save_news(articles):
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, "news.json")
    
    result = {
        "updated_at": datetime.now().isoformat(),
        "count": len(articles),
        "articles": articles
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

def main():
    all_articles = []
    
    for source, url in RSS_FEEDS:
        articles = fetch_rss_feed(url, source)
        all_articles.extend(articles)
    
    all_articles = deduplicate_articles(all_articles)
    all_articles.sort(key=lambda x: x.get("scraped_at", ""), reverse=True)
    
    save_news(all_articles)

if __name__ == "__main__":
    main()