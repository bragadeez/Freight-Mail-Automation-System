from mailer.html_utils import escape

def format_simple_table(rows: list, headers: list) -> str:
    """
    rows = list of lists
    headers = list
    """
    html = ['<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">']
    html.append("<tr>")
    for h in headers:
        html.append(f"<th>{escape(h)}</th>")
    html.append("</tr>")

    for row in rows:
        html.append("<tr>")
        for cell in row:
            html.append(f"<td>{escape(cell)}</td>")
        html.append("</tr>")

    html.append("</table>")
    return "\n".join(html)
