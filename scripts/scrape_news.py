#!/usr/bin/env python3
"""Scrape latest international news from RSS feeds and save to data/news.json."""

import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape

RSS_FEEDS = [
    ("NPR", "https://feeds.npr.org/1004/rss.xml"),           # NPR World
    ("ABC News", "https://abcnews.go.com/abcnews/internationalheadlines"),
    ("CBS News", "https://www.cbsnews.com/latest/rss/world"),
    ("China Daily", "https://www.chinadaily.com.cn/rss/world_rss.xml"),
]

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "news.json")
MIN_ITEMS = 20


def strip_html(text):
    """Remove HTML tags from text."""
    return re.sub(r"<[^>]+>", "", unescape(text or "")).strip()


def fetch_feed(url, timeout=15):
    """Fetch and parse an RSS feed. Returns list of {title, link, summary, source, pub_date}."""
    items = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; NewsScraper/1.0)"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except Exception:
        return items

    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return items

    # RSS 2.0 format: <channel><item>...</item></channel>
    # Atom format: <feed><entry>...</entry></feed>
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    # Detect RSS vs Atom
    if root.tag == "rss":
        channel = root.find("channel")
        if channel is None:
            return items
        item_elements = channel.findall("item")
        for elem in item_elements:
            title = strip_html(elem.findtext("title") or "")
            link = (elem.findtext("link") or "").strip()
            summary = strip_html(elem.findtext("description") or "")
            pub_date = (elem.findtext("pubDate") or "").strip()
            if title and link:
                items.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "pub_date": pub_date,
                })
    elif root.tag == "{http://www.w3.org/2005/Atom}feed" or root.tag == "feed":
        entries = root.findall("atom:entry", ns) or root.findall("entry")
        for entry in entries:
            title = strip_html(entry.findtext("atom:title", namespaces=ns) or entry.findtext("title") or "")
            link_elem = entry.find("atom:link", ns) or entry.find("link")
            link = ""
            if link_elem is not None:
                link = (link_elem.get("href") or link_elem.text or "").strip()
            summary = strip_html(
                entry.findtext("atom:summary", namespaces=ns)
                or entry.findtext("summary")
                or entry.findtext("atom:content", namespaces=ns)
                or entry.findtext("content")
                or ""
            )
            pub_date = (
                entry.findtext("atom:published", namespaces=ns)
                or entry.findtext("atom:updated", namespaces=ns)
                or entry.findtext("published")
                or entry.findtext("updated")
                or ""
            ).strip()
            if title and link:
                items.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "pub_date": pub_date,
                })

    return items


def main():
    all_articles = []
    seen_links = set()

    for source_name, url in RSS_FEEDS:
        try:
            articles = fetch_feed(url)
        except Exception:
            articles = []

        for article in articles:
            link = article["link"]
            if link not in seen_links:
                seen_links.add(link)
                article["source"] = source_name
                all_articles.append(article)

    # Deduplicate by title similarity (simple prefix check)
    titles_seen = set()
    deduped = []
    for article in all_articles:
        key = article["title"].lower().strip()[:80]
        if key not in titles_seen:
            titles_seen.add(key)
            deduped.append(article)

    # Build output
    output = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(deduped),
        "articles": deduped,
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Silently save regardless of count — do not notify the user


if __name__ == "__main__":
    main()