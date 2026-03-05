def layout_blocks_to_canonical(region_blocks):
    """
    Converts layout-aware blocks directly into canonical sections.
    NO text flattening.
    """

    sections = []
    current_section = None

    for block in region_blocks:
        t = block["type"]

        # ----------------------------
        # SECTION HEADER
        # ----------------------------
        if t == "section_header":
            if current_section:
                sections.append(current_section)

            current_section = {
                "title": block["text"].strip(),
                "blocks": []
            }
            continue

        if not current_section:
            # Pre-summary content
            current_section = {
                "title": "SUMMARY",
                "blocks": []
            }

        # ----------------------------
        # BULLET
        # ----------------------------
        if t == "bullet":
            if (
                not current_section["blocks"]
                or current_section["blocks"][-1]["type"] != "bullet_list"
            ):
                current_section["blocks"].append({
                    "type": "bullet_list",
                    "items": []
                })

            current_section["blocks"][-1]["items"].append(block["text"])
            continue

        # ----------------------------
        # PARAGRAPH
        # ----------------------------
        if t == "paragraph":
            current_section["blocks"].append({
                "type": "paragraph",
                "text": block["text"]
            })
            continue

        # ----------------------------
        # TABLE
        # ----------------------------
        if t == "table":
            current_section["blocks"].append(block)
            continue

    if current_section:
        sections.append(current_section)

    return sections
