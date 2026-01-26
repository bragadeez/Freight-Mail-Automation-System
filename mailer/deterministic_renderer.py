"""
Deterministic, email-safe HTML renderer.
Designed for Gmail + Outlook (desktop & web).
NO AI. NO conditional formatting. NO guessing.
"""

def render_email_html(report: dict) -> str:
    """
    report = {
        "week": "46",
        "region": "GCC",
        "sections": [
            {
                "title": "SUMMARY",
                "blocks": [...]
            }
        ]
    }
    """

    html = []

    # ==================================================
    # HTML + BODY
    # ==================================================
    html.append("""
    <html>
    <body style="margin:0;padding:0;background-color:#ffffff;">
    """)

    # ==================================================
    # 600px SAFE CONTAINER (CRITICAL FOR EMAIL)
    # ==================================================
    html.append("""
    <table width="600" align="center" cellpadding="0" cellspacing="0"
           style="
             width:600px;
             max-width:600px;
             margin:0 auto;
             font-family:Arial,Helvetica,sans-serif;
             font-size:14px;
             line-height:1.55;
             color:#000000;
           ">
      <tr>
        <td style="padding:20px;">
    """)

    # ==================================================
    # HEADER
    # ==================================================
    html.append(f"""
    <p style="margin:0 0 12px 0;">Dear Customer,</p>

    <p style="margin:0 0 16px 0;">
      Please find below the <b>Week {report['week']}</b> freight market update
      for <b>{report['region']}</b>.
    </p>
    """)

    # ==================================================
    # SECTIONS
    # ==================================================
    for section in report.get("sections", []):
        html.append(_render_section(section))

    # ==================================================
    # FOOTER
    # ==================================================
    html.append("""
    <p style="margin:24px 0 4px 0;">
      Best regards,<br>
      <b>Freight Market Intelligence Team</b>
    </p>
    """)

    # ==================================================
    # CLOSE CONTAINER
    # ==================================================
    html.append("""
        </td>
      </tr>
    </table>
    </body>
    </html>
    """)

    return "\n".join(html)


# ======================================================
# SECTION RENDERER
# ======================================================
def _render_section(section: dict) -> str:
    html = []

    # -------------------------
    # SECTION TITLE
    # -------------------------
    html.append(f"""
    <h3 style="
        margin-top:28px;
        margin-bottom:12px;
        font-size:16px;
        font-weight:bold;
        text-transform:uppercase;
        border-bottom:1px solid #cccccc;
        padding-bottom:4px;
    ">
      {section['title']}
    </h3>
    """)

    # -------------------------
    # BLOCKS
    # -------------------------
    for block in section.get("blocks", []):

        if block["type"] == "paragraph":
            html.append(_render_paragraph(block["text"]))

        elif block["type"] == "bullet_list":
            html.append(_render_bullet_list(block["items"]))

        elif block["type"] == "table":
            html.append(_render_table(block))

    return "\n".join(html)


# ======================================================
# PARAGRAPH
# ======================================================
def _render_paragraph(text: str) -> str:
    return f"""
    <p style="
        margin:6px 0 12px 0;
    ">
      {text}
    </p>
    """


# ======================================================
# BULLET LIST
# ======================================================
def _render_bullet_list(items: list) -> str:
    html = []

    html.append("""
    <ul style="
        margin:6px 0 14px 20px;
        padding:0;
    ">
    """)

    for item in items:
        html.append(f"""
        <li style="
            margin-bottom:8px;
            padding-left:2px;
        ">
          {item}
        </li>
        """)

    html.append("</ul>")

    return "\n".join(html)


# ======================================================
# TABLE
# ======================================================
def _render_table(block: dict) -> str:
    html = []

    html.append("""
    <table width="100%" cellpadding="0" cellspacing="0"
           style="
             border-collapse:collapse;
             margin:14px 0;
             font-size:13px;
           ">
      <tr>
    """)

    # -------------------------
    # HEADERS
    # -------------------------
    for header in block.get("headers", []):
        html.append(f"""
        <th style="
            border:1px solid #000000;
            background-color:#f2f2f2;
            font-weight:bold;
            text-align:left;
            padding:6px;
        ">
          {header}
        </th>
        """)

    html.append("</tr>")

    # -------------------------
    # ROWS
    # -------------------------
    for row in block.get("rows", []):
        html.append("<tr>")
        for cell in row:
            html.append(f"""
            <td style="
                border:1px solid #000000;
                padding:6px;
                vertical-align:top;
            ">
              {cell}
            </td>
            """)
        html.append("</tr>")

    html.append("</table>")

    return "\n".join(html)
