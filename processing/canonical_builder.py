import re


BULLET_PREFIXES = ("•", "-", "–", "o")


def build_canonical_report(
    *,
    week: str,
    region: str,
    section_text_map: dict
):
    """
    Converts raw section text into canonical structured format.

    section_text_map:
        {
            "SUMMARY": "raw text...",
            "OCEAN FREIGHT": "raw text..."
        }
    """

    report = {
        "week": week,
        "region": region,
        "sections": []
    }

    for section_title, raw_text in section_text_map.items():
        blocks = _parse_blocks(raw_text)

        report["sections"].append({
            "title": section_title,
            "blocks": blocks
        })

    return report


def _parse_blocks(text: str):
    """
    Breaks raw section text into paragraphs, bullet lists, and tables.
    Deterministic. No AI.
    """

    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    blocks = []

    current_paragraph = []
    current_bullets = []

    def flush_paragraph():
        nonlocal current_paragraph
        if current_paragraph:
            blocks.append({
                "type": "paragraph",
                "text": " ".join(current_paragraph).strip()
            })
            current_paragraph = []

    def flush_bullets():
        nonlocal current_bullets
        if current_bullets:
            blocks.append({
                "type": "bullet_list",
                "items": current_bullets
            })
            current_bullets = []

    for line in lines:
        stripped = line.strip()

        # Bullet
        if stripped.startswith(BULLET_PREFIXES):
            flush_paragraph()

            bullet_text = stripped.lstrip("•-–o ").strip()
            current_bullets.append(bullet_text)
            continue

        # Table row heuristic (multiple columns separated by spaces)
        if _looks_like_table_row(stripped):
            flush_paragraph()
            flush_bullets()

            _consume_table(blocks, lines, start_line=stripped)
            continue

        # Normal paragraph line
        flush_bullets()
        current_paragraph.append(stripped)

    flush_paragraph()
    flush_bullets()

    return blocks


def _looks_like_table_row(line: str) -> bool:
    # crude but reliable for freight PDFs
    return len(re.split(r"\s{2,}", line)) >= 2


def _consume_table(blocks, lines, start_line):
    """
    Build table block from consecutive table-like rows.
    """

    table_lines = []
    start_index = lines.index(start_line)

    for l in lines[start_index:]:
        if _looks_like_table_row(l):
            table_lines.append(l)
        else:
            break

    headers = re.split(r"\s{2,}", table_lines[0])
    rows = [
        re.split(r"\s{2,}", row)
        for row in table_lines[1:]
    ]

    blocks.append({
        "type": "table",
        "headers": headers,
        "rows": rows
    })
