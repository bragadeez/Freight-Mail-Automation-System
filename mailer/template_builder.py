from mailer.section_formatter import format_text_block
from mailer.html_utils import escape

def build_email_body_html(contact_name, region, region_content, week):
    name = contact_name if contact_name else "Customer"

    html_parts = []

    # Header
    html_parts.append(f"""
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 14px; color: #000;">
    <p>Dear {escape(name)},</p>

    <p>
      Please find below the <b>Week {week}</b> freight market update for
      <b>{escape(region)}</b>.
    </p>
    <hr>
    """)

    # Sections
    sections = region_content.get("sections", {})
    for section_name, content in sections.items():
        if not content:
            continue

        html_parts.append(f"<h3>{escape(section_name.upper())}</h3>")
        html_parts.append(format_text_block(content))

    # Footer
    html_parts.append("""
    <hr>
    <p>
      Best regards,<br>
      <b>Freight Market Intelligence Team</b>
    </p>
    </body>
    </html>
    """)

    return "\n".join(html_parts)
