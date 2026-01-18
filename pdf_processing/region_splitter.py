import re

TITLE_REGEX = re.compile(
    r"(Week\s+\d+\s+[–-]\s+(.+?)\s+Freight Market Update.*)",
    re.IGNORECASE
)

def split_by_subject(full_text: str):
    """
    Splits report by 'Week XX – <Region> Freight Market Update' lines.
    This matches how text is actually extracted from PDFs.
    """
    matches = list(TITLE_REGEX.finditer(full_text))
    regions = {}

    for i, match in enumerate(matches):
        title_line = match.group(1).strip()
        region = match.group(2).strip()

        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)

        body = full_text[start:end].strip()
        if not body:
            continue

        regions[region] = {
            "subject": title_line,
            "body": body
        }

    return regions
