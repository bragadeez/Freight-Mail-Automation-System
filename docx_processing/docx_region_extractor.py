from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
import json


# -------- Iterate blocks in correct order --------
def iter_block_items(parent):
    for child in parent.element.body.iterchildren():
        if child.tag.endswith('p'):
            yield Paragraph(child, parent)
        elif child.tag.endswith('tbl'):
            yield Table(child, parent)


# -------- Convert paragraph to HTML --------
def paragraph_to_html(p):
    text = p.text.strip()

    if text == "":
        return "<br>"

    if p.style.name.startswith("Heading"):
        return f"<h3>{text}</h3>"

    if "List Bullet" in p.style.name:
        return f"<li>{text}</li>"

    return f"<p>{text}</p>"


# -------- Convert table to HTML --------
def table_to_html(table):
    html = "<table border='1' cellspacing='0' cellpadding='6'>"
    for row in table.rows:
        html += "<tr>"
        for cell in row.cells:
            html += f"<td>{cell.text.strip()}</td>"
        html += "</tr>"
    html += "</table>"
    return html


# -------- Detect region name --------
def extract_region(text):

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


# -------- MAIN SPLITTER --------
def split_docx_to_regions(docx_path):

    doc = Document(docx_path)

    regions_html = {}
    current_region = None
    html_buffer = []

    for block in iter_block_items(doc):

        if isinstance(block, Paragraph):

            text = block.text.strip()

            if text.startswith("Subject:") or "Freight Market Update" in text:

                new_region = extract_region(text)

                if new_region:

                    if current_region:
                        regions_html[current_region] = "".join(html_buffer)

                    current_region = new_region
                    html_buffer = []

        if current_region:

            if isinstance(block, Paragraph):
                html_buffer.append(paragraph_to_html(block))

            elif isinstance(block, Table):
                html_buffer.append(table_to_html(block))

    if current_region:
        regions_html[current_region] = "".join(html_buffer)

    return regions_html