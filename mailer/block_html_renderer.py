from mailer.html_utils import escape

def render_blocks_to_html(blocks):
    html = []
    list_open = False

    def close_list():
        nonlocal list_open
        if list_open:
            html.append("</ul>")
            list_open = False

    for block in blocks:
        t = block["type"]

        if t == "title":
            close_list()
            html.append(f"<h2>{escape(block['text'])}</h2>")

        elif t == "section_header":
            close_list()
            html.append(f"<h3>{escape(block['text'])}</h3>")

        elif t == "separator":
            close_list()
            html.append("<hr>")

        elif t == "paragraph":
            close_list()
            html.append(f"<p>{escape(block['text'])}</p>")

        elif t == "bullet":
            if not list_open:
                html.append("<ul>")
                list_open = True
            html.append(f"<li>{escape(block['text'])}</li>")

        elif t == "table":
            close_list()
            html.append("""
            <table border="1" cellpadding="6" cellspacing="0"
                   style="border-collapse:collapse;width:100%;margin:16px 0;">
            """)
            html.append("<tr>")
            for h in block["headers"]:
                html.append(f"<th>{escape(h)}</th>")
            html.append("</tr>")

            for row in block["rows"]:
                html.append("<tr>")
                for cell in row:
                    html.append(f"<td>{escape(cell)}</td>")
                html.append("</tr>")

            html.append("</table>")

    close_list()
    return "\n".join(html)
