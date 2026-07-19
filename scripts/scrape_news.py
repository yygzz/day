#!/usr/bin/env python3

import os
import json
import feedparser
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse

RSS_FEEDS = [
    {"name": "NPR", "url": "https://feeds.npr.org/1001/rss.xml"},
    {"name": "ABC News", "url": "https://abcnews.go.com/abcnews/topstories"},
    {"name": "ABC News RSS", "url": "https://feeds.abcnews.com/abcnews/topstories"},
    {"name": "CBS News", "url": "https://www.cbsnews.com/latest/rss/main"},
    {"name": "China Daily", "url": "https://www.chinadaily.com.cn/rss/world.xml"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Reuters", "url": "http://feeds.reuters.com/reuters/topNews"},
    {"name": "CNN", "url": "http://rss.cnn.com/rss/edition.rss"},
    {"name": "New York Times", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"name": "Washington Post", "url": "https://www.washingtonpost.com/news/world/wp/feed/"},
]

TARGET_COUNT = 20
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
NEWS_FILE = os.path.join(DATA_DIR, "news.json")


def get_today_date():
    return datetime.now().strftime("%Y-%m-%d")


def parse_date(entry):
    for key in ["published", "updated", "pubDate", "dc_date"]:
        if key in entry:
            try:
                return feedparser.parse_date(entry[key])
            except:
                pass
    return datetime.now()


def is_today_news(entry):
    try:
        entry_date = parse_date(entry)
        today = datetime.now().date()
        return entry_date.date() == today
    except:
        return True


def extract_news_entry(feed_name, entry):
    title = entry.get("title", "").strip()
    link = entry.get("link", "").strip()
    summary = entry.get("summary", "") or entry.get("description", "") or ""
    summary = summary.strip()[:500]
    
    entry_date = parse_date(entry)
    
    source = feed_name
    if "NPR" in feed_name:
        source = "NPR"
    elif "ABC" in feed_name:
        source = "ABC News"
    elif "CBS" in feed_name:
        source = "CBS News"
    elif "China Daily" in feed_name:
        source = "China Daily"
    elif "BBC" in feed_name:
        source = "BBC News"
    elif "Reuters" in feed_name:
        source = "Reuters"
    elif "CNN" in feed_name:
        source = "CNN"
    elif "New York Times" in feed_name:
        source = "New York Times"
    elif "Washington Post" in feed_name:
        source = "Washington Post"
    
    return {
        "title": title,
        "link": link,
        "summary": summary,
        "source": source,
        "published_at": entry_date.strftime("%Y-%m-%d %H:%M:%S"),
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def fetch_rss_feed(feed):
    try:
        response = requests.get(feed["url"], timeout=10)
        response.raise_for_status()
        feed_data = feedparser.parse(response.content)
        return feed_data.entries
    except Exception:
        try:
            feed_data = feedparser.parse(feed["url"])
            return feed_data.entries
        except Exception:
            return []


def scrape_news():
    all_news = []
    seen_titles = set()
    seen_links = set()
    
    for feed in RSS_FEEDS:
        entries = fetch_rss_feed(feed)
        for entry in entries:
            news = extract_news_entry(feed["name"], entry)
            
            if not news["title"] or not news["link"]:
                continue
            
            if news["title"] in seen_titles:
                continue
            if news["link"] in seen_links:
                continue
            
            seen_titles.add(news["title"])
            seen_links.add(news["link"])
            
            if is_today_news(entry):
                all_news.append(news)
        
        if len(all_news) >= TARGET_COUNT:
            break
    
    if len(all_news) < TARGET_COUNT:
        for feed in RSS_FEEDS:
            entries = fetch_rss_feed(feed)
            for entry in entries:
                news = extract_news_entry(feed["name"], entry)
                
                if not news["title"] or not news["link"]:
                    continue
                
                if news["title"] in seen_titles:
                    continue
                if news["link"] in seen_links:
                    continue
                
                seen_titles.add(news["title"])
                seen_links.add(news["link"])
                all_news.append(news)
                
                if len(all_news) >= TARGET_COUNT:
                    return all_news
    
    return all_news


def save_news(news_list):
    os.makedirs(DATA_DIR, exist_ok=True)
    
    result = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(news_list),
        "news": news_list
    }
    
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def main():
    news_list = scrape_news()
    save_news(news_list)


if __name__ == "__main__":
    main()