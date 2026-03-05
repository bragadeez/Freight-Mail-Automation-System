from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
import re


# ---------------------------------------------------------
# Iterate document blocks in order
# ---------------------------------------------------------
def iter_block_items(parent):
    for child in parent.element.body.iterchildren():
        if child.tag.endswith('p'):
            yield Paragraph(child, parent)
        elif child.tag.endswith('tbl'):
            yield Table(child, parent)


# ---------------------------------------------------------
# Extract region from title
# ---------------------------------------------------------
def extract_region_from_title(text):

    if "Russia" in text:
        return "Russia"

    if "Europe" in text or "UK" in text:
        return "Europe & UK"

    if "GCC" in text:
        return "GCC"

    if "Turkey" in text:
        return "Turkey"

    if "United States" in text or "USA" in text:
        return "United States"

    return None


# ---------------------------------------------------------
# Main extractor (returns BLOCKS exactly like PDF version)
# ---------------------------------------------------------
def extract_layout_blocks(docx_path):

    doc = Document(docx_path)
    blocks = []

    for block in iter_block_items(doc):

        # --------------------------
        # Paragraph
        # --------------------------
        if isinstance(block, Paragraph):

            text = block.text.strip()

            if not text:
                continue

            # Title detection
            if text.startswith("Subject:") or "Freight Market Update" in text:
                blocks.append({
                    "type": "title",
                    "text": text
                })
                continue

            # Section header
            if text.isupper() and len(text) < 80:
                blocks.append({
                    "type": "section_header",
                    "text": text
                })
                continue

            # Bullet
            if "List Bullet" in block.style.name:
                blocks.append({
                    "type": "bullet",
                    "level": 1,
                    "text": text
                })
                continue

            # Paragraph
            blocks.append({
                "type": "paragraph",
                "text": text
            })

        # --------------------------
        # Table
        # --------------------------
        elif isinstance(block, Table):

            headers = [
                cell.text.strip()
                for cell in block.rows[0].cells
            ]

            rows = []

            for row in block.rows[1:]:
                rows.append([
                    cell.text.strip()
                    for cell in row.cells
                ])

            blocks.append({
                "type": "table",
                "headers": headers,
                "rows": rows
            })

    return blocks


# ---------------------------------------------------------
# Region splitter (same logic as old)
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