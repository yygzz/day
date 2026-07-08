import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional

RSS_SOURCES = [
    {"name": "NPR", "url": "https://www.npr.org/rss/rss.php?id=1001"},
    {"name": "ABC News", "url": "https://abcnews.go.com/abcnews/internationalheadlines"},
    {"name": "CBS News", "url": "https://www.cbsnews.com/latest/rss/world"},
    {"name": "China Daily", "url": "https://www.chinadaily.com.cn/rss/world_rss.xml"},
]

TARGET_COUNT = 20
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "news.json")


def fetch_rss(url: str, source_name: str) -> List[Dict]:
    news_items = []
    try:
        response = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        namespaces = {}
        
        for elem in root.iter():
            if "}" in elem.tag:
                prefix = elem.tag.split("}")[0].strip("{")
                if prefix not in namespaces:
                    namespaces[prefix] = elem.tag.split("}")[0].strip("{}")
        
        if namespaces:
            item_tag = f"{{{list(namespaces.values())[0]}}}item"
            title_tag = f"{{{list(namespaces.values())[0]}}}title"
            link_tag = f"{{{list(namespaces.values())[0]}}}link"
            pub_date_tag = f"{{{list(namespaces.values())[0]}}}pubDate"
            description_tag = f"{{{list(namespaces.values())[0]}}}description"
        else:
            item_tag = "item"
            title_tag = "title"
            link_tag = "link"
            pub_date_tag = "pubDate"
            description_tag = "description"
        
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        for item in root.iter(item_tag):
            try:
                title = item.findtext(title_tag) or ""
                link = item.findtext(link_tag) or ""
                pub_date_str = item.findtext(pub_date_tag) or ""
                description = item.findtext(description_tag) or ""
                
                if not title or not link:
                    continue
                
                pub_date = None
                if pub_date_str:
                    for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT",
                                "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"]:
                        try:
                            pub_date = datetime.strptime(pub_date_str, fmt)
                            break
                        except ValueError:
                            continue
                
                if pub_date:
                    pub_date = pub_date.date()
                    if pub_date < yesterday:
                        continue
                
                news_items.append({
                    "title": title.strip(),
                    "link": link.strip(),
                    "source": source_name,
                    "pub_date": pub_date_str.strip() if pub_date_str else "",
                    "description": description.strip()[:500] if description else "",
                    "scraped_at": datetime.now().isoformat()
                })
            except Exception:
                continue
    except Exception:
        pass
    
    return news_items


def main():
    all_news = []
    seen_titles = set()
    
    for source in RSS_SOURCES:
        items = fetch_rss(source["url"], source["name"])
        for item in items:
            title_key = item["title"].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                all_news.append(item)
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_news, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


if __name__ == "__main__":
    main()
