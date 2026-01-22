def extract_sections_from_lines(sections: dict, lines: list):
    extracted = {}
    ordered = [(k, v) for k, v in sections.items() if v is not None]
    ordered.sort(key=lambda x: x[1])

    for i, (section, start) in enumerate(ordered):
        start_idx = start - 1
        end_idx = (
            ordered[i + 1][1] - 1
            if i + 1 < len(ordered)
            else len(lines)
        )
        extracted[section] = "\n".join(
            lines[start_idx:end_idx]
        ).strip()

    return extracted
