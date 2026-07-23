import requests
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime, timedelta
from hashlib import md5

RSS_SOURCES = [
    {
        "name": "NPR",
        "url": "https://www.npr.org/rss/rss.php?id=1001",
        "language": "en"
    },
    {
        "name": "ABC News",
        "url": "https://abcnews.go.com/abcnews/topstories",
        "language": "en"
    },
    {
        "name": "CBS News",
        "url": "https://www.cbsnews.com/latest/rss/main",
        "language": "en"
    },
    {
        "name": "China Daily",
        "url": "http://www.chinadaily.com.cn/rss/world.xml",
        "language": "zh"
    },
    {
        "name": "BBC News",
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "language": "en"
    },
    {
        "name": "Reuters",
        "url": "https://www.reutersagency.com/feed/?best-topics=world&post-type=best",
        "language": "en"
    },
    {
        "name": "AP News",
        "url": "https://apnews.com/rss/world-news",
        "language": "en"
    },
    {
        "name": "The Guardian",
        "url": "https://www.theguardian.com/world/rss",
        "language": "en"
    },
    {
        "name": "CNN",
        "url": "http://rss.cnn.com/rss/edition_world.rss",
        "language": "en"
    },
    {
        "name": "Voice of America",
        "url": "https://www.voanews.com/api/zones/world/rss",
        "language": "en"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def parse_rss(xml_content, source_name, language):
    items = []
    try:
        root = ET.fromstring(xml_content)
        namespace = ""
        if root.tag.startswith("{"):
            namespace = root.tag.split("}")[0] + "}"
        
        for item in root.findall(f".//{namespace}item"):
            title = item.findtext(f"{namespace}title", "").strip()
            link = item.findtext(f"{namespace}link", "").strip()
            description = item.findtext(f"{namespace}description", "").strip()
            pub_date = item.findtext(f"{namespace}pubDate", "").strip()
            
            if not title or not link:
                continue
            
            items.append({
                "title": title,
                "link": link,
                "description": description,
                "source": source_name,
                "language": language,
                "pub_date": pub_date,
                "scraped_at": datetime.now().isoformat()
            })
    except Exception as e:
        pass
    return items

def fetch_rss(source):
    try:
        response = requests.get(source["url"], headers=HEADERS, timeout=10)
        response.raise_for_status()
        return parse_rss(response.content, source["name"], source["language"])
    except Exception as e:
        return []

def is_today_news(pub_date_str):
    if not pub_date_str:
        return True
    try:
        formats = [
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
            "%d %b %Y",
            "%B %d, %Y"
        ]
        for fmt in formats:
            try:
                pub_date = datetime.strptime(pub_date_str, fmt)
                if pub_date.tzinfo:
                    pub_date = pub_date.astimezone()
                    now = datetime.now(pub_date.tzinfo)
                else:
                    now = datetime.now()
                diff = now - pub_date
                return diff <= timedelta(days=2)
            except ValueError:
                continue
        return True
    except Exception:
        return True

def deduplicate(news_list):
    seen = set()
    unique = []
    for news in news_list:
        key = md5((news["title"] + news["link"]).encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            unique.append(news)
    return unique

def main():
    news_data = []
    
    for source in RSS_SOURCES:
        items = fetch_rss(source)
        news_data.extend(items)
    
    news_data = [n for n in news_data if is_today_news(n.get("pub_date"))]
    news_data = deduplicate(news_data)
    
    news_data.sort(key=lambda x: x.get("pub_date", ""), reverse=True)
    
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "news.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
