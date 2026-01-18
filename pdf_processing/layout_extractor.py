import pdfplumber
import re

BULLET_CHARS = ("•", "o", "-")

def extract_layout_blocks(pdf_path):
    """
    Extracts layout-aware semantic blocks from PDF.
    Returns a list of blocks preserving document order.
    """

    blocks = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # ---- 1. Extract tables first (so we don't double-read text)
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue

                headers = [h.strip() if h else "" for h in table[0]]
                rows = [
                    [c.strip() if c else "" for c in row]
                    for row in table[1:]
                ]

                blocks.append({
                    "type": "table",
                    "headers": headers,
                    "rows": rows
                })

            # ---- 2. Extract words with layout info
            words = page.extract_words(
                use_text_flow=True,
                keep_blank_chars=False,
                extra_attrs=["size", "fontname"]
            )

            if not words:
                continue

            # ---- 3. Group words into lines (by vertical position)
            lines = {}
            for w in words:
                top = round(w["top"], 1)
                lines.setdefault(top, []).append(w)

            for _, line_words in sorted(lines.items()):
                text = " ".join(w["text"] for w in line_words).strip()
                if not text:
                    continue

                sizes = [w.get("size", 0) for w in line_words if w.get("size")]
                avg_size = sum(sizes) / len(sizes) if sizes else 0

                # ---- TITLE (Week XX – Region Freight Market Update)
                if re.match(r"Week\s+\d+\s+[–-].+Freight Market Update", text):
                    blocks.append({
                        "type": "title",
                        "text": text
                    })
                    continue

                # ---- SECTION HEADERS (ALL CAPS / strong)
                if text.isupper() and len(text) < 80:
                    blocks.append({
                        "type": "section_header",
                        "text": text
                    })
                    continue

                # ---- SUBTEXT (parentheses lines)
                if text.startswith("(") and text.endswith(")"):
                    blocks.append({
                        "type": "subtext",
                        "text": text
                    })
                    continue

                # ---- BULLETS
                if text.startswith(BULLET_CHARS):
                    level = 1
                    if text.startswith("o"):
                        level = 2

                    clean = text.lstrip("•o-").strip()
                    blocks.append({
                        "type": "bullet",
                        "level": level,
                        "text": clean
                    })
                    continue

                # ---- PARAGRAPH (default)
                blocks.append({
                    "type": "paragraph",
                    "text": text
                })

    return blocks

def split_blocks_by_region(blocks):
    """
    Splits layout blocks into regions based on title blocks.
    Returns: { region_name: [blocks...] }
    """
    regions = {}
    current_region = None

    for block in blocks:
        if block["type"] == "title":
            text = block["text"]

            # Extract region name from title
            # Example: "Week 46 – Turkey Freight Market Update ..."
            if "–" in text:
                region = text.split("–", 1)[1].split("Freight")[0].strip()
                current_region = region
                regions[current_region] = [block]
            continue

        if current_region:
            regions[current_region].append(block)

    return regions
