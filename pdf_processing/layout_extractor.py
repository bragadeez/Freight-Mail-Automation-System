import pdfplumber
import re

BULLET_CHARS = ("•", "o", "-")

# ---------------------------------------------------------
# Extract region name cleanly from title
# ---------------------------------------------------------
def extract_region_from_title(text: str):
    text = re.sub(r"^\s*Subject:\s*", "", text, flags=re.I).strip()

    patterns = [
        r"Week\s+\d+\s*[–-]\s*(.+?)\s+Freight Market Update",
        r"(.+?)\s+Freight Market Update\s*[–-]\s*Week\s+\d+",
    ]

    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1).strip()

    return None


# ---------------------------------------------------------
# Main extractor
# ---------------------------------------------------------
def extract_layout_blocks(pdf_path):
    blocks = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:

            # ============================
            # TABLES (keep position-safe)
            # ============================
            tables = page.extract_tables()
            for table in tables or []:
                if not table or len(table) < 2:
                    continue

                headers = [c.strip() if c else "" for c in table[0]]
                rows = [
                    [c.strip() if c else "" for c in row]
                    for row in table[1:]
                ]

                blocks.append({
                    "type": "table",
                    "headers": headers,
                    "rows": rows
                })

            # ============================
            # WORDS → LINES
            # ============================
            words = page.extract_words(
                use_text_flow=True,
                keep_blank_chars=False,
                extra_attrs=["size"]
            )

            if not words:
                continue

            lines = {}
            for w in words:
                top = round(w["top"], 1)
                lines.setdefault(top, []).append(w)

            # ============================
            # LINE CLASSIFICATION
            # ============================
            for _, line_words in sorted(lines.items()):
                text = " ".join(w["text"] for w in line_words).strip()
                if not text:
                    continue

                # ----------------------------
                # SEPARATOR
                # ----------------------------
                if re.fullmatch(r"[─\-]{10,}", text):
                    blocks.append({"type": "separator"})
                    continue

                # ----------------------------
                # TITLE
                # ----------------------------
                if re.search(r"Freight Market Update", text, re.I) and re.search(r"Week\s+\d+", text):
                    blocks.append({"type": "title", "text": text})
                    continue

                # ----------------------------
                # SECTION HEADER
                # ----------------------------
                if text.isupper() and len(text) < 80:
                    blocks.append({"type": "section_header", "text": text})
                    continue

                # ----------------------------
                # BULLET (explicit symbols)
                # ----------------------------
                if text.startswith(BULLET_CHARS):
                    clean = text.lstrip("•o-").strip()
                    blocks.append({
                        "type": "bullet",
                        "level": 1,
                        "text": clean
                    })
                    continue

                # ----------------------------
                # PARAGRAPH (default)
                # ----------------------------
                blocks.append({
                    "type": "paragraph",
                    "text": text
                })

    return normalize_blocks(blocks)


# ---------------------------------------------------------
# Region splitter
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

        if current_region:
            regions[current_region].append(block)

    return regions


# ---------------------------------------------------------
# NORMALIZATION (THIS IS THE REAL FIX)
# ---------------------------------------------------------
def normalize_blocks(blocks):
    normalized = []

    for block in blocks:
        if not normalized:
            normalized.append(block)
            continue

        prev = normalized[-1]

        # -----------------------------------
        # Bullet continuation (CRITICAL FIX)
        # -----------------------------------
        if (
            block["type"] == "paragraph"
            and prev["type"] == "bullet"
            and not block["text"].isupper()
        ):
            prev["text"] += " " + block["text"]
            continue

        # -----------------------------------
        # Paragraph continuation
        # -----------------------------------
        if (
            block["type"] == "paragraph"
            and prev["type"] == "paragraph"
            and not prev["text"].endswith(".")
        ):
            prev["text"] += " " + block["text"]
            continue

        # -----------------------------------
        # Arrow / bracket continuation
        # -----------------------------------
        if (
            block["type"] == "paragraph"
            and block["text"].startswith(("(", "↑", "↓"))
            and prev["type"] in ("bullet", "paragraph")
        ):
            prev["text"] += " " + block["text"]
            continue

        normalized.append(block)

    return normalized
