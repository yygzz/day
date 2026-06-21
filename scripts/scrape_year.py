import urllib.request
import urllib.error
import re
import json
import time
import random
from html.parser import HTMLParser
from datetime import datetime, timedelta

class EventExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_h2 = False
        self.in_p = False
        self.current_h2 = ''
        self.current_p = ''
        self.events = []

    def handle_starttag(self, tag, attrs):
        if tag == 'h2':
            self.in_h2 = True
            self.current_h2 = ''
        elif tag == 'p':
            self.in_p = True
            self.current_p = ''

    def handle_endtag(self, tag):
        if tag == 'h2':
            self.in_h2 = False
            match = re.match(r'(\d{1,4})\s*[:\.]\s*(.+)', self.current_h2.strip())
            if match:
                self.events.append({
                    'year': match.group(1),
                    'title': match.group(2).strip(),
                    'description': ''
                })
        elif tag == 'p':
            self.in_p = False
            if self.events and not self.events[-1]['description']:
                desc = self.current_p.strip()
                if desc and len(desc) > 20:
                    self.events[-1]['description'] = desc

    def handle_data(self, data):
        if self.in_h2:
            self.current_h2 += data
        elif self.in_p:
            self.current_p += data


def fetch_page(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code} for {url}")
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def classify_event(title):
    title_lower = title.lower()
    if any(w in title_lower for w in ['war', 'battle', 'invasion', 'attack', 'siege', 'military', 'army', 'navy', 'revolution', 'independence', 'constitution', 'treaty', 'election', 'president', 'king', 'queen', 'emperor', 'empire', 'republic', 'assassination', 'executed', 'dies', 'born', 'invasion']):
        return 'politics'
    if any(w in title_lower for w in ['invented', 'computer', 'internet', 'phone', 'airplane', 'telegraph', 'radio', 'television', 'rocket', 'satellite', 'nuclear', 'electricity', 'engine']):
        return 'technology'
    if any(w in title_lower for w in ['discover', 'space', 'moon', 'mars', 'planet', 'star', 'galaxy', 'dna', 'atom', 'vaccine', 'medicine', 'doctor', 'scientist']):
        return 'science'
    if any(w in title_lower for w in ['olympics', 'world cup', 'championship', 'baseball', 'football', 'basketball', 'soccer', 'tennis', 'boxing', 'race', 'marathon', 'medal']):
        return 'sports'
    if any(w in title_lower for w in ['protest', 'strike', 'rights', 'feminist', 'abolition', 'slavery', 'demonstration', 'march', 'boycott']):
        return 'society'
    if any(w in title_lower for w in ['festival', 'holiday', 'christmas', 'easter', 'thanksgiving', 'halloween', 'new year', 'independence day']):
        return 'holiday'
    return 'culture'


def generate_id(title, year, month, day):
    safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-').lower()[:30]
    return f"{safe_title}-{year}-{month:02d}-{day:02d}"


def month_name(month):
    names = ['january', 'february', 'march', 'april', 'may', 'june',
             'july', 'august', 'september', 'october', 'november', 'december']
    return names[month - 1]


def main():
    all_events = []
    start_date = datetime(2024, 1, 1)
    total_days = 366  # 2024 is a leap year

    for i in range(total_days):
        current = start_date + timedelta(days=i)
        month = current.month
        day = current.day
        url = f"https://allthatsinteresting.com/today-in-history/{month_name(month)}-{day}"

        print(f"Fetching {month:02d}-{day:02d}...")
        html = fetch_page(url)
        if not html:
            continue

        parser = EventExtractor()
        parser.feed(html)

        # Take up to 4 events per day
        for idx, ev in enumerate(parser.events[:4]):
            category = classify_event(ev['title'])
            all_events.append({
                'id': generate_id(ev['title'], ev['year'], month, day),
                'date': f"{month:02d}-{day:02d}",
                'year': int(ev['year']) if ev['year'].isdigit() else 0,
                'title': ev['title'],
                'description': ev['description'][:220] if ev['description'] else f"On this day in {ev['year']}, {ev['title']}.",
                'category': category,
                'image': '',  # Will use category fallback
                'theme': {
                    'gradient': '',  # Will use category fallback
                    'textColor': 'light'
                }
            })

        time.sleep(random.uniform(0.5, 1.5))

    output = {'events': all_events}
    with open('/workspace/data/events.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nTotal events scraped: {len(all_events)}")
    print("Saved to /workspace/data/events.json")


if __name__ == '__main__':
    main()
