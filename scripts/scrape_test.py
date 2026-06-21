import urllib.request
import urllib.error
import re
from html.parser import HTMLParser

class EventExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_h2 = False
        self.in_p = False
        self.current_h2 = ''
        self.current_p = ''
        self.events = []
        self.skip_first_p = False

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
                    'title': match.group(2),
                    'description': ''
                })
        elif tag == 'p':
            self.in_p = False
            if self.events and not self.events[-1]['description']:
                desc = self.current_p.strip()
                if desc and len(desc) > 20:
                    self.events[-1]['description'] = desc[:250]

    def handle_data(self, data):
        if self.in_h2:
            self.current_h2 += data
        elif self.in_p:
            self.current_p += data

url = 'https://allthatsinteresting.com/today-in-history/june-21'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as response:
        html = response.read().decode('utf-8', errors='ignore')

    parser = EventExtractor()
    parser.feed(html)

    for ev in parser.events[:5]:
        print(ev)
    print(f"Total events found: {len(parser.events)}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
except Exception as e:
    print(f"Error: {e}")
