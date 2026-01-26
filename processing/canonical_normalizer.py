import re


SEMANTIC_BULLET_PREFIXES = (
    "Rates:",
    "Capacity:",
    "Demand:",
    "Space:",
    "Transit:",
    "Outlook:",
    "Equipment:",
)


def normalize_sections(sections: list):
    """
    Input: sections from canonical_builder
    Output: cleaned / normalized sections
    """
    normalized = []

    for section in sections:
        blocks = _normalize_blocks(section["blocks"])
        normalized.append({
            "title": section["title"],
            "blocks": blocks
        })

    return normalized


def _normalize_blocks(blocks: list):
    output = []
    i = 0

    while i < len(blocks):
        block = blocks[i]

        # -------------------------------
        # Bullet continuation fix
        # -------------------------------
        if block["type"] == "bullet_list":
            items = block["items"]

            # Look ahead for paragraph continuation
            if i + 1 < len(blocks):
                next_block = blocks[i + 1]
                if next_block["type"] == "paragraph":
                    items[-1] += " " + next_block["text"]
                    i += 1  # consume paragraph

            output.append({
                "type": "bullet_list",
                "items": items
            })
            i += 1
            continue

        # -------------------------------
        # Semantic bullet conversion
        # -------------------------------
        if block["type"] == "paragraph":
            lines = re.split(r"[.;]\s+", block["text"])

            if all(
                line.strip().startswith(SEMANTIC_BULLET_PREFIXES)
                for line in lines
            ):
                output.append({
                    "type": "bullet_list",
                    "items": [l.strip() for l in lines]
                })
                i += 1
                continue

        # -------------------------------
        # Default: keep block
        # -------------------------------
        output.append(block)
        i += 1

    return output
