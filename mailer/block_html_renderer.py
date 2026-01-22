from mailer.html_utils import escape

def render_blocks_to_html(blocks):
    html = []
    list_stack = []

    def close_lists(target_level=0):
        nonlocal list_stack
        while len(list_stack) > target_level:
            html.append("</ul>")
            list_stack.pop()

    for block in blocks:
        btype = block["type"]

        # ------------------------------------------------
        # TITLE
        # ------------------------------------------------
        if btype == "title":
            close_lists()
            html.append(
                f"<h2 style='margin:22px 0 12px;'>"
                f"{escape(block['text'])}</h2>"
            )

        # ------------------------------------------------
        # SECTION HEADER
        # ------------------------------------------------
        elif btype == "section_header":
            close_lists()
            html.append(
                f"<h3 style='margin:26px 0 10px; border-bottom:1px solid #ddd;'>"
                f"{escape(block['text'])}</h3>"
            )

        # ------------------------------------------------
        # SUBTEXT
        # ------------------------------------------------
        elif btype == "subtext":
            close_lists()
            html.append(
                f"<p style='margin:4px 0 10px; color:#555; font-style:italic;'>"
                f"{escape(block['text'])}</p>"
            )

        # ------------------------------------------------
        # PARAGRAPH
        # ------------------------------------------------
        elif btype == "paragraph":
            close_lists()
            html.append(
                f"<p style='margin:6px 0 10px; line-height:1.45;'>"
                f"{escape(block['text'])}</p>"
            )

        # ------------------------------------------------
        # BULLETS (PROPERLY SPACED)
        # ------------------------------------------------
        elif btype == "bullet":
            level = block.get("level", 1)

            while len(list_stack) < level:
                html.append(
                    "<ul style='margin:6px 0 14px 20px; padding-left:12px;'>"
                )
                list_stack.append("ul")

            close_lists(level)

            html.append(
                f"<li style='margin-bottom:8px; line-height:1.45;'>"
                f"{escape(block['text'])}</li>"
            )

        # ------------------------------------------------
        # TABLE (EMAIL-SAFE)
        # ------------------------------------------------
        elif btype == "table":
            close_lists()
            html.append("""
            <table width="100%" cellpadding="6" cellspacing="0"
                   style="
                     border-collapse:collapse;
                     font-size:13px;
                     margin:18px 0;
                     border:1px solid #ccc;
                   ">
            """)

            # headers
            html.append("<tr>")
            for h in block.get("headers", []):
                html.append(
                    f"<th style='border:1px solid #ccc;"
                    f"background:#f2f2f2;"
                    f"text-align:left;'>"
                    f"{escape(h)}</th>"
                )
            html.append("</tr>")

            # rows
            for row in block.get("rows", []):
                html.append("<tr>")
                for cell in row:
                    html.append(
                        f"<td style='border:1px solid #ccc;"
                        f"vertical-align:top;'>"
                        f"{escape(cell)}</td>"
                    )
                html.append("</tr>")

            html.append("</table>")

        # ------------------------------------------------
        # SEPARATOR
        # ------------------------------------------------
        elif btype == "separator":
            close_lists()
            html.append("<hr style='margin:26px 0;'>")

        elif btype == "paragraph":
            close_lists()
            html.append(
                f"<p style='margin:10px 0; line-height:1.5;'>"
                f"{escape(block['text'])}</p>"
            )

    close_lists()
    return "\n".join(html)
