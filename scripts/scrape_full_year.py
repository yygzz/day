import urllib.request
import urllib.error
import re
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = 'https://allthatsinteresting.com/today-in-history'
MONTHS = [
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
]


def fetch_page(url, retries=2):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"  Error fetching {url} (attempt {attempt + 1}): {e}")
            time.sleep(1)
    return None


def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&quot;', '"').replace('&#039;', "'")
    text = text.replace('&#8220;', '"').replace('&#8221;', '"')
    text = text.replace('&#8216;', "'").replace('&#8217;', "'")
    text = text.replace('&#8211;', '-').replace('&#8212;', '-')
    text = text.replace('&#8230;', '...').replace('&amp;', '&')
    text = text.replace('&nbsp;', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_year_title(text):
    text = clean_text(text)
    if not text:
        return None, None

    # "1735: Paul Revere Is Born"
    # "1755/57: Alexander Hamilton Is Born"
    # "41 A.D.: Claudius Is Declared Emperor"
    # "37 C.E.: Caligula Becomes Emperor"
    # "49 B.C.E: Julius Caesar Crosses The Rubicon"
    # "357 C.E. Emperor Constantius II Arrives In Rome"
    match = re.match(
        r'^(\d{1,4})(?:\s*/\s*\d{1,2})?\s*(?:A\.D\.|B\.C\.E?\.?|C\.E\.?|B\.C\.)?\s*[\.:\-]?\s*(.+)$',
        text, re.IGNORECASE
    )
    if match and match.group(2).strip():
        return match.group(1), match.group(2).strip()

    # Fallback: first number then delimiter
    match = re.match(r'^(\d{1,4})\s*[\.:\-]\s*(.+)$', text)
    if match:
        return match.group(1), match.group(2).strip()

    # No year found
    return '0', text


def classify_event(title, description=''):
    text = (title + ' ' + description).lower()

    holiday_words = ['christmas', 'easter', 'thanksgiving', 'halloween', 'new year', 'independence day', 'may day', 'festival']
    if any(w in text for w in holiday_words):
        return 'holiday'

    sports_words = ['olympics', 'world cup', 'championship', 'baseball', 'football', 'basketball',
                    'soccer', 'tennis', 'boxing', 'marathon', 'medal', 'athlete', 'fifa', 'nfl', 'nba', 'tournament']
    if any(w in text for w in sports_words):
        return 'sports'

    society_words = ['protest', 'strike', 'rights', 'feminist', 'abolition', 'slavery',
                     'demonstration', 'march', 'boycott', 'civil rights', "women's", 'gay rights',
                     'human rights', 'apartheid', 'labor union']
    if any(w in text for w in society_words):
        return 'society'

    politics_words = ['war', 'battle', 'invasion', 'siege', 'military', 'army', 'navy',
                      'revolution', 'independence', 'constitution', 'treaty', 'election',
                      'president', 'prime minister', 'king', 'queen', 'emperor', 'empire',
                      'republic', 'assassination', 'executed', 'coup', 'monarchy', 'parliament',
                      'congress', 'dictator', 'occupation', 'surrender', 'allies', 'axis']
    if any(w in text for w in politics_words):
        return 'politics'

    tech_patterns = [r'\binvented\b', r'\bcomputer\b', r'\binternet\b', r'\btelephone\b',
                     r'\bairplane\b', r'\btelegraph\b', r'\bradio\b', r'\btelevision\b',
                     r'\brocket\b', r'\bsatellite\b', r'\bnuclear\b', r'\belectricity\b',
                     r'\bengine\b', r'\bsoftware\b', r'\bwebsite\b', r'\brobot\b',
                     r'\bartificial intelligence\b']
    if any(re.search(p, text) for p in tech_patterns):
        return 'technology'

    science_words = ['discover', 'spacecraft', 'moon landing', 'planet', 'star', 'galaxy',
                     'dna', 'atom', 'vaccine', 'medicine', 'scientist', 'physics', 'chemistry',
                     'biology', 'evolution', 'relativity', 'theory']
    if any(w in text for w in science_words):
        return 'science'

    culture_words = ['painting', 'painter', 'artist', 'music', 'musician', 'composer',
                     'writer', 'novel', 'poem', 'film', 'movie', 'actor', 'theater',
                     'book', 'published', 'art', 'museum', 'sculpture', 'author', 'play']
    if any(w in text for w in culture_words):
        return 'culture'

    if re.search(r'\b(born|dies|died|death)\b', text):
        return 'politics'

    return 'culture'


def generate_id(title, year, month, day, index):
    safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-').lower()[:30]
    return f"{safe_title}-{year}-{month:02d}-{day:02d}-{index}"


def extract_events_from_day(html, month, day):
    article_match = re.search(r'<article class="post-content" itemprop="articleBody">(.*?)</article>', html, re.DOTALL)
    if not article_match:
        return []

    article = article_match.group(1)
    # Remove the calendar widget
    article = re.sub(r'<div class="tih-calendar".*?</div>', '', article, flags=re.DOTALL, count=1)

    parts = re.split(r'(<h2[^>]*>.*?</h2>)', article, flags=re.DOTALL)
    events = []

    for i in range(1, len(parts), 2):
        heading = clean_text(parts[i])
        content = parts[i + 1] if i + 1 < len(parts) else ''

        if not heading:
            continue

        # Skip the introductory/dek heading
        if re.search(r'what happened (today|on this day) in history', heading, re.IGNORECASE):
            continue

        year, title = parse_year_title(heading)
        if not title:
            continue

        year_int = int(year) if year.isdigit() else 0

        # Find first image after the heading (exclude tiny icons)
        img_match = re.search(r'<img[^>]+src="(https?://[^"]+)"[^>]*>', content)
        image = ''
        if img_match:
            src = img_match.group(1)
            # Prefer a reasonably sized image if srcset is available
            srcset_match = re.search(r'srcset="([^"]+)"', img_match.group(0))
            if srcset_match:
                candidates = [s.strip() for s in srcset_match.group(1).split(',')]
                best = None
                best_width = 0
                for cand in candidates:
                    pieces = cand.split()
                    if len(pieces) == 2:
                        url, width_str = pieces
                        width = int(re.search(r'\d+', width_str).group()) if re.search(r'\d+', width_str) else 0
                        if width >= 600 and (best is None or width < best_width):
                            best = url
                            best_width = width
                if best:
                    src = best
            image = src

        # Find first meaningful paragraph (skip captions/credits)
        description = ''
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL)
        for p in paragraphs:
            # Skip caption paragraphs
            if re.search(r'class="[^"]*wp-caption-text[^"]*"', p):
                continue
            ptext = clean_text(p)
            if len(ptext) > 30 and not re.match(r'^(Wikimedia Commons|Public Domain|Shutterstock|Getty Images|Library of Congress)', ptext, re.IGNORECASE):
                description = ptext
                break

        if not description:
            description = f"On this day in {year}, {title}."

        category = classify_event(title, description)

        events.append({
            'title': title,
            'year': year_int,
            'description': description,
            'image': image,
            'category': category
        })

    return events


def build_slug_list():
    slugs = []
    for month_idx, month in enumerate(MONTHS, 1):
        days_in_month = 31
        if month_idx == 2:
            days_in_month = 29
        elif month_idx in [4, 6, 9, 11]:
            days_in_month = 30
        for day in range(1, days_in_month + 1):
            slugs.append((month_idx, day, f"{month}-{day}"))
    return slugs


def scrape_one(args):
    month, day, slug = args
    url = f"{BASE_URL}/{slug}"
    html = fetch_page(url)
    if not html:
        print(f"  Failed to fetch {slug}", flush=True)
        return []

    day_events = extract_events_from_day(html, month, day)
    print(f"  {slug}: {len(day_events)} events", flush=True)

    results = []
    for idx, ev in enumerate(day_events):
        results.append({
            'id': generate_id(ev['title'], ev['year'], month, day, idx),
            'date': f"{month:02d}-{day:02d}",
            'year': ev['year'],
            'title': ev['title'],
            'description': ev['description'],
            'category': ev['category'],
            'image': ev['image'],
            'theme': {
                'gradient': '',
                'textColor': 'light'
            }
        })
    return results


def main():
    slugs = build_slug_list()
    all_events = []
    completed = 0

    print(f"Starting scrape of {len(slugs)} days ...", flush=True)
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(scrape_one, s): s for s in slugs}
        for future in as_completed(futures):
            day_events = future.result()
            all_events.extend(day_events)
            completed += 1
            if completed % 50 == 0:
                print(f"Progress: {completed}/{len(slugs)} days, {len(all_events)} events so far", flush=True)

    # Sort by date for stable output
    all_events.sort(key=lambda e: (e['date'], e['year']))

    output = {'events': all_events}
    with open('/workspace/data/events.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nTotal events saved: {len(all_events)}", flush=True)


if __name__ == '__main__':
    main()
