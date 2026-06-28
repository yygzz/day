import urllib.request
import urllib.error
import re
import json
import random
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET

RSS_FEEDS = [
    ('BBC', 'http://feeds.bbci.co.uk/news/rss.xml'),
    ('Reuters', 'https://www.reutersagency.com/feed/?best-topics=news'),
    ('NPR', 'https://feeds.npr.org/1001/rss.xml'),
    ('AP News', 'https://webfeeds.ap.org/apnews/TopNews'),
    ('The Guardian', 'https://www.theguardian.com/uk/rss'),
]

SOURCE_RELIABILITY = {
    'BBC': 9, 'Reuters': 10, 'AP News': 10, 'NPR': 8,
    'The Guardian': 8, '新华社': 9, 'CCTV': 8, '中国新闻网': 7,
    '联合国': 10, '美联社': 10
}

CATEGORY_KEYWORDS = {
    'politics': ['president', 'election', 'parliament', 'government', 'minister', 'diplomatic', 'summit', 'vote', 'political'],
    'conflict': ['war', 'attack', 'strike', 'military', 'ceasefire', 'drone', 'missile', 'killed', 'conflict'],
    'economy': ['tariff', 'trade', 'economy', 'market', 'stock', 'inflation', 'finance', 'investment'],
    'technology': ['ai', 'artificial intelligence', 'tech', 'cyber', 'software', 'chip', 'semiconductor'],
    'science': ['climate', 'space', 'vaccine', 'study', 'research', 'scientists'],
    'society': ['human rights', 'refugee', 'aid', 'protest', 'women', 'children', 'health'],
    'culture': ['museum', 'art', 'film', 'music', 'heritage', 'festival'],
    'sports': ['world cup', 'olympics', 'championship', 'tennis', 'football', 'basketball']
}


def fetch_feed(url, retries=1):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    for _ in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f'  Feed error {url}: {e}')
    return None


def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_rss(xml, source):
    items = []
    try:
        root = ET.fromstring(xml)
        channel = root.find('channel')
        if channel is None:
            return items
        for item in channel.findall('item'):
            title = item.find('title')
            desc = item.find('description')
            link = item.find('link')
            pub_date = item.find('pubDate')
            if title is None:
                continue
            items.append({
                'title': clean_text(title.text or ''),
                'summary': clean_text(desc.text or '')[:180],
                'url': link.text if link is not None else '',
                'date': pub_date.text if pub_date is not None else '',
                'source': source
            })
    except Exception as e:
        print(f'  Parse error for {source}: {e}')
    return items


def classify(title, summary):
    text = (title + ' ' + summary).lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for k in keywords if k in text)
    if max(scores.values(), default=0) == 0:
        return 'politics'
    return max(scores, key=scores.get)


def generate_evaluation(title, summary, category):
    templates = {
        'politics': '此事牵动国际政治格局，后续发展值得持续关注，相关方表态将成为关键变量。',
        'conflict': '冲突升级风险仍存，人道影响令人担忧，国际社会斡旋空间备受考验。',
        'economy': '事件对全球贸易与金融市场具有信号意义，企业和投资者需密切跟踪政策走向。',
        'technology': '技术突破与产业变革交织，既带来效率提升，也引发治理与伦理新议题。',
        'science': '科学研究再次揭示人类面临的共同挑战，跨国合作与政策响应尤为关键。',
        'society': '社会议题反映深层结构性矛盾，舆论与政策互动将塑造后续走向。',
        'culture': '文化交流与遗产保护牵动公众情感，也是国家软实力的重要体现。',
        'sports': '体育事件激发全球关注，竞技之外亦承载着民族情绪与商业价值。'
    }
    return templates.get(category, '该事件具有国际影响，后续进展值得留意。')


def rate_importance(title, summary, category):
    text = (title + summary).lower()
    score = 5
    if any(w in text for w in ['war', 'attack', 'ceasefire', 'summit', 'tariff', 'trade war', 'president']):
        score += 2
    if category in ['conflict', 'politics', 'economy']:
        score += 1
    return min(10, score)


def generate_id(title):
    safe = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-').lower()[:25]
    return safe or 'news-' + str(random.randint(1000, 9999))


def main():
    all_items = []
    for source, url in RSS_FEEDS:
        print(f'Fetching {source} ...')
        xml = fetch_feed(url)
        if not xml:
            continue
        items = parse_rss(xml, source)
        print(f'  Got {len(items)} items')
        for it in items[:8]:
            category = classify(it['title'], it['summary'])
            all_items.append({
                'id': generate_id(it['title']),
                'title': it['title'],
                'summary': it['summary'],
                'evaluation': generate_evaluation(it['title'], it['summary'], category),
                'reliability': SOURCE_RELIABILITY.get(source, 7),
                'importance': rate_importance(it['title'], it['summary'], category),
                'time': datetime.now().strftime('%Y-%m-%d'),
                'location': '国际',
                'people': '',
                'source': source,
                'sourceUrl': it['url'],
                'category': category,
                'image': ''
            })

    # Deduplicate by title similarity
    seen = set()
    unique = []
    for item in all_items:
        key = item['title'].lower()[:40]
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    unique.sort(key=lambda x: x['importance'], reverse=True)

    output = {'news': unique}
    with open('/workspace/data/news.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f'\nSaved {len(unique)} news items')


if __name__ == '__main__':
    main()
