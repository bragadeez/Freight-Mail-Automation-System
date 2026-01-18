from mailer.html_utils import escape

def format_text_block(text: str) -> str:
    """
    Converts a raw section into HTML paragraphs and bullet lists
    """
    lines = text.splitlines()
    html_lines = []
    in_list = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Bullet points
        if line.startswith("•"):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{escape(line[1:].strip())}</li>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<p>{escape(line)}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)