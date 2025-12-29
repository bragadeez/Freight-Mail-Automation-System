import re

def split_by_region(pages_text: dict, regions: list):
    combined_text = "\n".join(pages_text.values())
    region_blocks = {}

    for i, region in enumerate(regions):
        pattern = re.escape(region)
        match = re.search(pattern, combined_text, re.IGNORECASE)

        if not match:
            continue

        start = match.start()
        end = (
            re.search(re.escape(regions[i + 1]), combined_text, re.IGNORECASE).start()
            if i + 1 < len(regions)
            and re.search(re.escape(regions[i + 1]), combined_text, re.IGNORECASE)
            else len(combined_text)
        )

        region_blocks[region] = combined_text[start:end].strip()

    return region_blocks
