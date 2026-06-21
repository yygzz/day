import json
import re

CREDIT_PREFIXES = re.compile(
    r'^(Wikimedia Commons|Public Domain|Shutterstock|Getty Images|Library of Congress|National Archives|Alamy|Reuters|AP Images?|Courtesy of)[\s:.,]+',
    re.IGNORECASE
)

CREDIT_PREFIXES_NO_SPACE = re.compile(
    r'^(Wikimedia Commons|Public Domain|Shutterstock|Getty Images|Library of Congress|National Archives|Alamy|Reuters|AP Images?|Courtesy of)',
    re.IGNORECASE
)


def clean_description(text):
    text = text.strip()
    text = CREDIT_PREFIXES.sub('', text)
    text = CREDIT_PREFIXES_NO_SPACE.sub('', text)
    return text.strip()


def main():
    with open('/workspace/data/events.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned = 0
    for event in data['events']:
        new_desc = clean_description(event['description'])
        if new_desc != event['description']:
            event['description'] = new_desc
            cleaned += 1

    with open('/workspace/data/events.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'Cleaned {cleaned} descriptions')


if __name__ == '__main__':
    main()
