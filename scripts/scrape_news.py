import os
import json
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

RSS_FEEDS = [
    {
        "name": "NPR",
        "url": "https://feeds.npr.org/1001/rss.xml",
        "min_quota": 3
    },
    {
        "name": "ABC News",
        "url": "https://abcnews.go.com/abcnews/topstories",
        "min_quota": 3,
        "type": "html"
    },
    {
        "name": "CBS News",
        "url": "https://www.cbsnews.com/latest/rss/main",
        "min_quota": 3
    },
    {
        "name": "China Daily",
        "url": "https://www.chinadaily.com.cn/rss/world_rss.xml",
        "min_quota": 3
    },
    {
        "name": "BBC News",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "min_quota": 3
    },
    {
        "name": "Reuters",
        "url": "https://www.reutersagency.com/feed/?best-topics=world-news&post-type=best",
        "min_quota": 3
    },
    {
        "name": "CNN",
        "url": "http://rss.cnn.com/rss/edition_world.rss",
        "min_quota": 3
    }
]

TARGET_TOTAL = 20
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def get_today_date_str():
    return datetime.now().strftime("%Y-%m-%d")

def parse_rss_feed(url, source_name):
    news_items = []
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")
        
        for item in items:
            title = item.title.get_text(strip=True) if item.title else ""
            link = item.link.get_text(strip=True) if item.link else ""
            pub_date = item.pubDate.get_text(strip=True) if item.pubDate else ""
            description = item.description.get_text(strip=True) if item.description else ""
            
            if title and link:
                news_items.append({
                    "title": title,
                    "link": link,
                    "source": source_name,
                    "pub_date": pub_date,
                    "description": description,
                    "scraped_at": datetime.now().isoformat()
                })
    except Exception:
        pass
    return news_items

def parse_abc_html(url, source_name):
    news_items = []
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all("article")
        
        for article in articles:
            anchor = article.find("a")
            title_elem = article.find("h2") or article.find("h3")
            
            if anchor and title_elem:
                title = title_elem.get_text(strip=True)
                link = anchor.get("href")
                if link and not link.startswith("http"):
                    link = "https://abcnews.go.com" + link
                
                if title and link:
                    news_items.append({
                        "title": title,
                        "link": link,
                        "source": source_name,
                        "pub_date": "",
                        "description": "",
                        "scraped_at": datetime.now().isoformat()
                    })
    except Exception:
        pass
    return news_items

def extract_date_from_url(url):
    url_patterns = [
        r"/(\d{4})/(\d{2})/(\d{2})/",
        r"/a/(\d{4})(\d{2})(\d{2})/"
    ]
    
    for pattern in url_patterns:
        match = re.search(pattern, url)
        if match:
            try:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                return datetime(year, month, day)
            except Exception:
                pass
    return None

def is_today_news(pub_date_str, url=""):
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    current_year = today.year
    
    date_patterns = [
        r"(\d{4})-(\d{2})-(\d{2})",
        r"(\w{3}), (\d{2}) (\w{3}) (\d{4})",
        r"(\d{2}) (\w{3}) (\d{4})"
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, pub_date_str)
        if match:
            try:
                if len(match.groups()) == 3:
                    day, month, year = match.groups()
                    month_num = datetime.strptime(month, "%b").month
                    news_date = datetime(int(year), month_num, int(day))
                else:
                    year, month, day = match.groups()
                    news_date = datetime(int(year), int(month), int(day))
                
                if news_date.date() == today.date() or news_date.date() == yesterday.date():
                    return True
            except Exception:
                pass
    
    url_date = extract_date_from_url(url)
    if url_date:
        if url_date.year != current_year and url_date.year != current_year - 1:
            return False
        if url_date.date() == today.date() or url_date.date() == yesterday.date():
            return True
    
    return False

def deduplicate_news(news_list):
    seen = set()
    unique = []
    
    for news in news_list:
        key = news["title"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(news)
    
    return unique

def scrape_all_news():
    all_news = []
    
    for feed in RSS_FEEDS:
        source_name = feed["name"]
        url = feed["url"]
        min_quota = feed.get("min_quota", 0)
        
        try:
            if feed.get("type") == "html":
                items = parse_abc_html(url, source_name)
            else:
                items = parse_rss_feed(url, source_name)
            
            today_items = [item for item in items if is_today_news(item["pub_date"], item.get("link", ""))]
            
            all_news.extend(today_items)
        except Exception:
            pass
    
    return all_news

def main():
    os.makedirs("data", exist_ok=True)
    
    news_list = scrape_all_news()
    
    news_list = deduplicate_news(news_list)
    
    news_list = sorted(news_list, key=lambda x: x["scraped_at"], reverse=True)
    
    result = {
        "scraped_at": datetime.now().isoformat(),
        "total_count": len(news_list),
        "news": news_list
    }
    
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()