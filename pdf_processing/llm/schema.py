ALLOWED_SECTIONS = [
    "SUMMARY",
    "OCEAN FREIGHT",
    "AIR FREIGHT",
    "MULTIMODAL",
    "POLITICAL & REGULATORY",
    "CLIMATE & WEATHER",
    "ADVISORY"
]

def validate_llm_output(data: dict, total_lines: int):
    if "sections" not in data:
        raise ValueError("Missing sections key")

    seen = []

    for section, line in data["sections"].items():
        if section not in ALLOWED_SECTIONS:
            raise ValueError(f"Invalid section: {section}")

        if line is not None:
            if not isinstance(line, int):
                raise ValueError(f"{section} line not int")

            if line < 1 or line > total_lines:
                raise ValueError(f"{section} line out of bounds")

            seen.append(line)

    if seen != sorted(seen):
        raise ValueError("Sections not in order")
