from mailer.block_html_renderer import render_blocks_to_html
from mailer.html_utils import escape

def build_email_body_html(contact_name, region, region_blocks, week):
    name = contact_name if contact_name else "Customer"

    html_parts = []

    html_parts.append(f"""
    <html>
    <body style="
    font-family: Arial, sans-serif;
    font-size: 14px;
    line-height: 1.5;
    color: #000;
">

    <p>Dear {escape(name)},</p>

    <p>
      Please find below the freight market update{" for Week " + week if week != "UNKNOWN" else ""} for
      <b>{escape(region)}</b>.
    </p>
    <hr>
    """)

    # ⬇️ CORE CHANGE: render blocks directly
    html_parts.append(render_blocks_to_html(region_blocks))

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
