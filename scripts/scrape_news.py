#!/usr/bin/env python3
"""Scrape latest international news from RSS feeds and save to data/news.json."""

import json
import os
import re
import hashlib
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from xml.etree import ElementTree

FEEDS = [
    "https://feeds.npr.org/1004/rss.xml",
    "https://abcnews.go.com/abcnews/internationalheadlines",
    "https://www.cbsnews.com/latest/rss/world",
    "https://www.chinadaily.com.cn/rss/world_rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
]

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "news.json")
MIN_ARTICLES = 20


def fetch_feed(url, timeout=15):
    """Fetch and parse an RSS feed, return list of article dicts."""
    articles = []
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 NewsScraper/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            tree = ElementTree.fromstring(resp.read())
        # Handle namespaces
        ns = {"dc": "http://purl.org/dc/elements/1.1/",
              "content": "http://purl.org/rss/1.0/modules/content/",
              "media": "http://search.yahoo.com/mrss/"}

        for item in tree.iter("item"):
            title = _text(item, "title")
            link = _text(item, "link")
            description = _text(item, "description")
            pub_date = _text(item, "pubDate") or _text(item, "dc:date", ns)
            if not title:
                continue
            articles.append({
                "title": _clean(title),
                "link": link.strip() if link else "",
                "description": _clean(description)[:500] if description else "",
                "pub_date": pub_date.strip() if pub_date else "",
            })
    except Exception:
        pass
    return articles


def _text(element, tag, ns=None):
    """Get text content of a child element."""
    child = element.find(tag, ns) if ns else element.find(tag)
    if child is not None and child.text:
        return child.text
    return ""


def _clean(text):
    """Strip HTML tags and whitespace."""
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def _dedupe(articles):
    """Remove duplicate articles based on title similarity."""
    seen = set()
    unique = []
    for a in articles:
        key = hashlib.md5(a["title"].lower().encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    all_articles = []
    for url in FEEDS:
        all_articles.extend(fetch_feed(url))

    all_articles = _dedupe(all_articles)

    now = datetime.now(timezone.utc).isoformat()
    result = {
        "updated": now,
        "count": len(all_articles),
        "articles": all_articles[:max(MIN_ARTICLES, len(all_articles))],
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
