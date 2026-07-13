#!/usr/bin/env python3
"""Scrape latest international news from RSS feeds and save to data/news.json."""

import json
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

OUTPUT_FILE = Path(__file__).resolve().parent.parent / "data" / "news.json"

RSS_FEEDS = [
    "https://feeds.npr.org/1004/rss.xml",
    "https://feeds.npr.org/1001/rss.xml",
    "https://abcnews.go.com/abcnews/internationalheadlines",
    "https://www.cbsnews.com/latest/rss/international",
    "https://www.chinadaily.com.cn/rss/world_rss.xml",
    "https://feeds.npr.org/1006/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
]

MIN_ARTICLES = 20


def fetch_rss(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_rss(xml_text: str) -> list[dict]:
    articles = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return articles

    # Handle RSS 2.0
    for item in root.iter("item"):
        title = _text(item, "title")
        link = _text(item, "link")
        desc = _text(item, "description")
        pub_date = _text(item, "pubDate")
        if title and link:
            articles.append({
                "title": _clean(title),
                "link": link.strip(),
                "description": _clean(desc),
                "pubDate": pub_date.strip() if pub_date else "",
            })

    # Handle Atom feeds
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall(".//atom:entry", ns):
        title = _text(entry, "title")
        link_el = entry.find("atom:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        desc_el = entry.find("atom:summary", ns) or entry.find("atom:content", ns)
        desc = desc_el.text.strip() if desc_el is not None and desc_el.text else ""
        pub_date = _text(entry, "published") or _text(entry, "updated") or ""
        if title and link:
            articles.append({
                "title": _clean(title),
                "link": link.strip(),
                "description": _clean(desc),
                "pubDate": pub_date.strip(),
            })

    return articles


def _text(el: ET.Element, tag: str) -> str:
    child = el.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return ""


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def dedup(articles: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for a in articles:
        key = hashlib.md5(a["title"].lower().encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            result.append(a)
    return result


def main():
    all_articles: list[dict] = []

    for feed_url in RSS_FEEDS:
        try:
            xml_text = fetch_rss(feed_url)
            articles = parse_rss(xml_text)
            all_articles.extend(articles)
        except Exception:
            continue

    all_articles = dedup(all_articles)

    output = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "count": len(all_articles),
        "articles": all_articles,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
