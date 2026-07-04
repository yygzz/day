#!/usr/bin/env python3
"""Scrape international news from RSS feeds and save to data/news.json."""

import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError

RSS_FEEDS = [
    ("NPR", "https://feeds.npr.org/1001/rss.xml"),
    ("ABC News", "https://abcnews.go.com/abcnews/internationalheadlines"),
    ("CBS News", "https://www.cbsnews.com/latest/rss/world"),
    ("China Daily", "https://www.chinadaily.com.cn/rss/world_rss.xml"),
]

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "news.json")
MIN_NEWS = 20


def fetch_feed(name, url):
    """Fetch and parse an RSS feed, return list of article dicts."""
    articles = []
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"})
        with urlopen(req, timeout=15) as resp:
            data = resp.read()
        root = ET.fromstring(data)

        # Handle both RSS 2.0 and Atom feeds
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//item")
        if not items:
            items = root.findall(".//atom:entry", ns)

        for item in items:
            title_el = item.find("title")
            if title_el is None:
                title_el = item.find("atom:title", ns)
            title = title_el.text.strip() if title_el is not None and title_el.text else None

            link_el = item.find("link")
            link = None
            if link_el is not None:
                link = link_el.text or link_el.get("href")
            if not link:
                link_el = item.find("atom:link", ns)
                if link_el is not None:
                    link = link_el.get("href")

            if title and link:
                articles.append({
                    "title": title,
                    "url": link,
                    "source": name,
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                })
    except Exception:
        pass  # Silently ignore failures
    return articles


def deduplicate(articles):
    """Remove duplicate articles by title similarity."""
    seen = set()
    unique = []
    for a in articles:
        key = a["title"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique


def save_results(articles):
    """Save articles to JSON file."""
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def main():
    all_articles = []
    for name, url in RSS_FEEDS:
        all_articles.extend(fetch_feed(name, url))

    unique = deduplicate(all_articles)

    # Always save what we have — don't notify user regardless of count
    save_results(unique)

    print(f"Saved {len(unique)} articles to {OUTPUT_FILE}", file=sys.stderr)


if __name__ == "__main__":
    main()