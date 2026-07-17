import os
import json
import time
import hashlib
import requests
import xml.etree.ElementTree as ET

RSS_FEEDS = [
    {"name": "NPR", "url": "https://feeds.npr.org/1001/rss.xml"},
    {"name": "ABC News", "url": "https://abcnews.go.com/abcnews/topstories"},
    {"name": "CBS News", "url": "https://www.cbsnews.com/latest/rss/main"},
    {"name": "China Daily", "url": "http://www.chinadaily.com.cn/rss/world.xml"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Reuters", "url": "https://www.reutersagency.com/feed/?best-topics=world&post_type=best"},
    {"name": "CNN", "url": "http://rss.cnn.com/rss/edition_world.rss"},
    {"name": "The New York Times", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def fetch_rss(feed):
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(feed["url"], headers=headers, timeout=15)
        response.raise_for_status()
        return response.content
    except Exception:
        return None

def parse_rss(content, source_name):
    news_items = []
    try:
        root = ET.fromstring(content)
        channel = root.find("channel")
        if channel is None:
            return news_items
        
        for item in channel.findall("item"):
            title = ""
            link = ""
            pub_date = ""
            description = ""
            
            title_elem = item.find("title")
            if title_elem is not None and title_elem.text:
                title = title_elem.text.strip()
            
            link_elem = item.find("link")
            if link_elem is not None and link_elem.text:
                link = link_elem.text.strip()
            
            pub_date_elem = item.find("pubDate")
            if pub_date_elem is not None and pub_date_elem.text:
                pub_date = pub_date_elem.text.strip()
            
            desc_elem = item.find("description")
            if desc_elem is not None and desc_elem.text:
                description = desc_elem.text.strip()[:500]
            
            if title and link:
                news_items.append({
                    "title": title,
                    "link": link,
                    "source": source_name,
                    "pub_date": pub_date,
                    "description": description,
                    "timestamp": time.time()
                })
    except Exception:
        pass
    return news_items

def generate_id(title, link):
    text = f"{title}{link}"
    return hashlib.md5(text.encode()).hexdigest()

def main():
    all_news = []
    seen_ids = set()
    
    for feed in RSS_FEEDS:
        content = fetch_rss(feed)
        if content is None:
            continue
        
        items = parse_rss(content, feed["name"])
        for item in items:
            item_id = generate_id(item["title"], item["link"])
            if item_id not in seen_ids:
                seen_ids.add(item_id)
                item["id"] = item_id
                all_news.append(item)
    
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "news.json")
    
    result = {
        "count": len(all_news),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "news": all_news
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()