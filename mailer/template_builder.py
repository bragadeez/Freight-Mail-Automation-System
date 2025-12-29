def build_email_body(contact_name, region, region_content, week):
    lines = []

    # Greeting
    name = contact_name if contact_name else "Customer"
    lines.append(f"Dear {name},\n")

    # Intro
    lines.append(
        f"Please find below the Week {week} freight market update for {region}.\n"
    )

    # Insert sections EXACTLY
    sections = region_content.get("sections", {})
    for key, content in sections.items():
        if content:
            lines.append(content.strip())
            lines.append("\n")

    # Sign-off
    lines.append(
        "Best regards,\n"
        "Freight Market Intelligence Team\n"
    )

    return "\n".join(lines)
