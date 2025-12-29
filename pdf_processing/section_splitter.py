import re
from config.constants import SECTION_KEYWORDS

def split_sections(region_text: str):
    sections = {}
    positions = []

    # Find section header positions
    for section, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            match = re.search(re.escape(kw), region_text, re.IGNORECASE)
            if match:
                positions.append((match.start(), section, kw))
                break

    # Sort by appearance in text
    positions.sort(key=lambda x: x[0])

    for i, (start, section, kw) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(region_text)
        content = region_text[start:end].strip()
        sections[section] = content

    return sections
