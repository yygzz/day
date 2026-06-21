import json
import re


def classify_event(title, description=''):
    text = (title + ' ' + description).lower()

    # Holiday / festival (highest priority because of named days)
    holiday_words = ['christmas', 'easter', 'thanksgiving', 'halloween', 'new year', 'independence day', 'may day', 'festival']
    if any(w in text for w in holiday_words):
        return 'holiday'

    # Sports
    sports_words = ['olympics', 'world cup', 'championship', 'baseball', 'football', 'basketball',
                    'soccer', 'tennis', 'boxing', 'marathon', 'medal', 'athlete', 'fifa', 'nfl', 'nba', 'tournament']
    if any(w in text for w in sports_words):
        return 'sports'

    # Society / rights
    society_words = ['protest', 'strike', 'rights', 'feminist', 'abolition', 'slavery',
                     'demonstration', 'march', 'boycott', 'civil rights', "women's", 'gay rights',
                     'human rights', 'apartheid', 'labor union']
    if any(w in text for w in society_words):
        return 'society'

    # Politics / war / governance
    politics_words = ['war', 'battle', 'invasion', 'siege', 'military', 'army', 'navy',
                      'revolution', 'independence', 'constitution', 'treaty', 'election',
                      'president', 'prime minister', 'king', 'queen', 'emperor', 'empire',
                      'republic', 'assassination', 'executed', 'coup', 'monarchy', 'parliament',
                      'congress', 'dictator', 'occupation', 'surrender', 'allies', 'axis']
    if any(w in text for w in politics_words):
        return 'politics'

    # Technology — use word boundaries to avoid false positives like "engineer" -> "engine"
    tech_patterns = [r'\binvented\b', r'\bcomputer\b', r'\binternet\b', r'\btelephone\b',
                     r'\bairplane\b', r'\btelegraph\b', r'\bradio\b', r'\btelevision\b',
                     r'\brocket\b', r'\bsatellite\b', r'\bnuclear\b', r'\belectricity\b',
                     r'\bengine\b', r'\bsoftware\b', r'\bwebsite\b', r'\brobot\b',
                     r'\bartificial intelligence\b']
    if any(re.search(p, text) for p in tech_patterns):
        return 'technology'

    # Science
    science_words = ['discover', 'spacecraft', 'moon landing', 'planet', 'star', 'galaxy',
                     'dna', 'atom', 'vaccine', 'medicine', 'scientist', 'physics', 'chemistry',
                     'biology', 'evolution', 'relativity', 'theory']
    if any(w in text for w in science_words):
        return 'science'

    # Culture
    culture_words = ['painting', 'painter', 'artist', 'music', 'musician', 'composer',
                     'writer', 'novel', 'poem', 'film', 'movie', 'actor', 'theater',
                     'book', 'published', 'art', 'museum', 'sculpture', 'author', 'play']
    if any(w in text for w in culture_words):
        return 'culture'

    # Default politics for people/dates that are clearly historical figures
    if re.search(r'\b(born|dies|died|death)\b', text):
        return 'politics'

    return 'culture'


def main():
    with open('/workspace/data/events.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for event in data['events']:
        event['category'] = classify_event(event['title'], event.get('description', ''))

    with open('/workspace/data/events.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    counts = {}
    for event in data['events']:
        counts[event['category']] = counts.get(event['category'], 0) + 1
    print('Reclassified categories:', counts)


if __name__ == '__main__':
    main()
