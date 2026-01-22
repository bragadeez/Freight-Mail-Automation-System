import pdfplumber
import re

BULLET_CHARS = ("•", "o", "-")

# ---------------------------------------------------------
# Helper: Extract region name from title (ROBUST)
# ---------------------------------------------------------
def extract_region_from_title(text: str):
    """
    Extracts region name from title line.
    Handles:
    - 'Subject: Week 46 – Turkey Freight Market Update'
    - 'Europe & UK Freight Market Update – Week 46'
    - 'Subject: China & Hong Kong Freight Market Update – Week 46'
    """

    # -------------------------------------------------
    # 1. HARD CLEAN: remove leading 'Subject:'
    # -------------------------------------------------
    clean_text = re.sub(
        r"^\s*Subject:\s*",
        "",
        text,
        flags=re.IGNORECASE
    ).strip()

    # -------------------------------------------------
    # 2. REGION EXTRACTION (both title formats)
    # -------------------------------------------------
    patterns = [
        r"Week\s+\d+\s*[–-]\s*(.+?)\s+Freight Market Update",
        r"(.+?)\s+Freight Market Update\s*[–-]\s*Week\s+\d+"
    ]

    for p in patterns:
        m = re.search(p, clean_text, re.IGNORECASE)
        if m:
            return m.group(1).strip()

    return None



# ---------------------------------------------------------
# MAIN: Layout-aware block extraction
# ---------------------------------------------------------
def extract_layout_blocks(pdf_path):
    """
    Extracts semantic, layout-aware blocks from PDF.
    Preserves order and structure exactly as document.
    """

    blocks = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:

            # =================================================
            # 1. TABLE EXTRACTION (MERGED PER PAGE)
            # =================================================
            tables = page.extract_tables()

            if tables:
                merged_headers = None
                merged_rows = []

                for table in tables:
                    if not table or len(table) < 2:
                        continue

                    headers = [h.strip() if h else "" for h in table[0]]
                    rows = [
                        [c.strip() if c else "" for c in row]
                        for row in table[1:]
                    ]

                    if not merged_headers:
                        merged_headers = headers

                    merged_rows.extend(rows)

                if merged_headers and merged_rows:
                    blocks.append({
                        "type": "table",
                        "headers": merged_headers,
                        "rows": merged_rows
                    })

            # =================================================
            # 2. WORD EXTRACTION WITH LAYOUT METADATA
            # =================================================
            words = page.extract_words(
                use_text_flow=True,
                keep_blank_chars=False,
                extra_attrs=["size", "fontname"]
            )

            if not words:
                continue

            # Group words into lines (by vertical position)
            lines = {}
            for w in words:
                top = round(w["top"], 1)
                lines.setdefault(top, []).append(w)

            # =================================================
            # 3. LINE-BY-LINE CLASSIFICATION
            # =================================================
            for _, line_words in sorted(lines.items()):
                text = " ".join(w["text"] for w in line_words).strip()
                if not text:
                    continue

                # -------------------------------------------------
                # FIX 4: SECTION SEPARATORS (PDF horizontal lines)
                # -------------------------------------------------
                # Detect long lines of ───── or ------
                if re.match(r"^[─\-]{10,}$", text):
                    blocks.append({
                        "type": "separator"
                    })
                    continue

                # -------------------------------------------------
                # TITLE (MUST BE FIRST, OVERRIDES EVERYTHING)
                # -------------------------------------------------
                if re.search(
                    r"Week\s+\d+\s*[–-]\s*.+?Freight Market Update",
                    text,
                    re.IGNORECASE
                ) or re.search(
                    r".+?Freight Market Update\s*[–-]\s*Week\s+\d+",
                    text,
                    re.IGNORECASE
                ):
                    blocks.append({
                        "type": "title",
                        "text": text
                    })
                    continue

                # -------------------------------------------------
                # SECTION HEADERS (ALL CAPS, SHORT)
                # -------------------------------------------------
                if text.isupper() and len(text) < 80:
                    blocks.append({
                        "type": "section_header",
                        "text": text
                    })
                    continue

                # -------------------------------------------------
                # SUBTEXT (Parentheses)
                # -------------------------------------------------
                if text.startswith("(") and text.endswith(")"):
                    blocks.append({
                        "type": "subtext",
                        "text": text
                    })
                    continue

                # -------------------------------------------------
                # BULLETS (• o -)
                # -------------------------------------------------
                if text.startswith(BULLET_CHARS):
                    level = 2 if text.startswith("o") else 1
                    clean = text.lstrip("•o-").strip()

                    blocks.append({
                        "type": "bullet",
                        "level": level,
                        "text": clean
                    })
                    continue

                # -------------------------------------------------
                # FIX 2: COLON-STYLE BULLETS (Key: Value)
                # -------------------------------------------------
                if ":" in text:
                    left, right = text.split(":", 1)
                    if len(left.strip()) < 40:
                        blocks.append({
                            "type": "bullet",
                            "level": 1,
                            "text": f"{left.strip()}: {right.strip()}"
                        })
                        continue

                # Continuation line (starts with arrow / bracket)
                if text.startswith(("(", "↑", "↓")) and blocks:
                    last = blocks[-1]
                    if last["type"] in ("bullet", "paragraph"):
                        last["text"] += " " + text
                        continue

                
                # -------------------------------------------------
                # PARAGRAPH (DEFAULT FALLBACK)
                # -------------------------------------------------
                if blocks and is_continuation(blocks[-1], {"text": text}):
                    blocks[-1]["text"] += " " + text
                else:
                    blocks.append({
                        "type": "paragraph",
                        "text": text
                    })


    return normalize_blocks(blocks)


# ---------------------------------------------------------
# SPLIT BLOCKS BY REGION (TITLE-DRIVEN)
# ---------------------------------------------------------
def split_blocks_by_region(blocks):
    regions = {}
    current_region = None

    for block in blocks:
        if block["type"] == "title":
            region = extract_region_from_title(block["text"])
            if region:
                current_region = region
                regions[current_region] = [block]
            continue

        # 🔒 Everything after a title belongs to that region
        if current_region:
            regions[current_region].append(block)

    return regions


def normalize_blocks(blocks):
    """
    Merge continuation lines into previous logical block.
    Fixes broken bullets, paragraphs, and spacing.
    """
    normalized = []

    for block in blocks:
        if not normalized:
            normalized.append(block)
            continue

        prev = normalized[-1]

        # --------------------------------------------------
        # 1. Bullet continuation
        # --------------------------------------------------
        if (
            block["type"] == "paragraph"
            and prev["type"] == "bullet"
            and not block["text"].isupper()
        ):
            prev["text"] += " " + block["text"]
            continue

        # --------------------------------------------------
        # 2. Paragraph continuation
        # --------------------------------------------------
        if (
            block["type"] == "paragraph"
            and prev["type"] == "paragraph"
            and not prev["text"].endswith(".")
        ):
            prev["text"] += " " + block["text"]
            continue

        # --------------------------------------------------
        # 3. Arrow / bracket continuation
        # --------------------------------------------------
        if (
            block["type"] == "paragraph"
            and block["text"].startswith(("(", "↑", "↓"))
            and prev["type"] in ("bullet", "paragraph")
        ):
            prev["text"] += " " + block["text"]
            continue

        normalized.append(block)

    return normalized

def is_continuation(prev, current):
    return (
        prev
        and prev["type"] in ("bullet", "paragraph")
        and not current["text"].startswith(("•", "o", "-", "("))
        and current["text"][0].islower()
    )
