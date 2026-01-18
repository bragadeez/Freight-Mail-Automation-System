from mailer.html_utils import escape

def render_blocks_to_html(blocks):
    """
    Converts semantic layout blocks into HTML.
    """
    html = []
    list_stack = []

    def close_lists(target_level=0):
        nonlocal list_stack
        while len(list_stack) > target_level:
            html.append("</ul>")
            list_stack.pop()

    for block in blocks:
        btype = block["type"]

        # ---------------- TITLE ----------------
        if btype == "title":
            close_lists()
            html.append(f"<h2>{escape(block['text'])}</h2>")

        # ---------------- SECTION HEADER ----------------
        elif btype == "section_header":
            close_lists()
            html.append(f"<h3>{escape(block['text'])}</h3>")

        # ---------------- SUBTEXT ----------------
        elif btype == "subtext":
            close_lists()
            html.append(f"<p><i>{escape(block['text'])}</i></p>")

        # ---------------- PARAGRAPH ----------------
        elif btype == "paragraph":
            close_lists()
            html.append(f"<p>{escape(block['text'])}</p>")

        # ---------------- BULLETS ----------------
        elif btype == "bullet":
            level = block.get("level", 1)

            while len(list_stack) < level:
                html.append("<ul>")
                list_stack.append("ul")

            close_lists(level)

            html.append(f"<li>{escape(block['text'])}</li>")

        # ---------------- TABLE ----------------
        elif btype == "table":
            close_lists()
            html.append(
                '<table border="1" cellpadding="6" cellspacing="0" '
                'style="border-collapse:collapse; width:100%;">'
            )

            # Headers
            html.append("<tr>")
            for h in block.get("headers", []):
                html.append(f"<th>{escape(h)}</th>")
            html.append("</tr>")

            # Rows
            for row in block.get("rows", []):
                html.append("<tr>")
                for cell in row:
                    html.append(f"<td>{escape(cell)}</td>")
                html.append("</tr>")

            html.append("</table>")

    close_lists()
    return "\n".join(html)