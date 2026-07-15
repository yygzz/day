import os
import json
import datetime
import hashlib
import time
import feedparser
import requests

RSS_SOURCES = [
    {"name": "NPR", "url": "https://www.npr.org/rss/rss.php?id=1001"},
    {"name": "ABC News", "url": "https://abcnews.go.com/abcnews/topstories"},
    {"name": "CBS News", "url": "https://www.cbsnews.com/latest/rss/main"},
    {"name": "China Daily", "url": "http://www.chinadaily.com.cn/rss/world_rss.xml"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Reuters", "url": "http://feeds.reuters.com/reuters/topNews"},
    {"name": "CNN", "url": "http://rss.cnn.com/rss/edition_world.rss"},
]

TARGET_COUNT = 20
OUTPUT_FILE = "../data/news.json"


def get_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def parse_date(date_str):
    if not date_str:
        return None
    date_formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%a, %d %b %Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
    ]
    for fmt in date_formats:
        try:
            parsed = datetime.datetime.strptime(date_str, fmt)
            if parsed.tzinfo:
                return parsed.astimezone(datetime.timezone.utc)
            return parsed.replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            continue
    return None


def is_recent(date_str, hours=24):
    parsed = parse_date(date_str)
    if parsed is None:
        return False
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    delta = now_utc - parsed
    return delta.total_seconds() >= 0 and delta.total_seconds() <= hours * 3600


def fetch_rss(source):
    news_items = []
    try:
        resp = requests.get(source["url"], timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)

        if not feed.entries:
            return news_items

        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary", "").strip()
            published = entry.get("published", "")

            if not title or not link:
                continue

            if not is_recent(published):
                continue

            news_items.append({
                "title": title,
                "link": link,
                "summary": summary,
                "source": source["name"],
                "published": published,
                "hash": get_hash(title + link)
            })
    except Exception:
        pass
    return news_items


def main():
    all_news = []
    seen_hashes = set()

    for source in RSS_SOURCES:
        items = fetch_rss(source)
        for item in items:
            if item["hash"] not in seen_hashes:
                seen_hashes.add(item["hash"])
                all_news.append(item)
        time.sleep(1)

    all_news.sort(key=lambda x: x.get("published", ""), reverse=True)

    output_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()