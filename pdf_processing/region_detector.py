import re

REGION_PATTERNS = {
    "United States": [r"\bUnited States\b", r"\bUSA\b"],
    "Europe & UK": [r"Europe\s*&\s*UK", r"\bEurope\b", r"\bUK\b"],
    "GCC": [r"\bGCC\b"],
    "India": [r"\bIndia\b"],
    "China": [r"\bChina\b"],
    "Hong Kong": [r"Hong\s*Kong"],
    "Russia": [r"\bRussia\b"],
    "Turkey": [r"\bTurkey\b"],
}

def detect_regions(pages_text: dict):
    detected = set()

    for page_text in pages_text.values():
        if not page_text:
            continue

        for region, patterns in REGION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, page_text, re.IGNORECASE):
                    detected.add(region)
                    break

    return sorted(detected)
