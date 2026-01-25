import re
from pdf_processing.llm.section_prompt import build_section_prompt
from pdf_processing.llm.gemini_client import gemini_llm


SECTION_NAMES = [
    "SUMMARY",
    "OCEAN FREIGHT",
    "AIR FREIGHT",
    "MULTIMODAL",
    "POLITICAL & REGULATORY",
    "CLIMATE & WEATHER",
    "ADVISORY"
]


def _parse_llm_output(text: str) -> dict:
    """
    Parse Gemini output like:
    SUMMARY: 2
    OCEAN FREIGHT: 14
    MULTIMODAL: NONE
    """
    sections = {}

    for line in text.splitlines():
        if ":" not in line:
            continue

        name, value = line.split(":", 1)
        name = name.strip().upper()
        value = value.strip()

        if name not in SECTION_NAMES:
            continue

        if value.upper() == "NONE":
            sections[name] = None
        else:
            try:
                sections[name] = int(value)
            except ValueError:
                sections[name] = None

    return sections


def _regex_fallback_lines(lines: list) -> dict:
    """
    Deterministic fallback using exact section headers
    """
    found = {}

    for idx, line in enumerate(lines):
        clean = line.strip().upper()

        for section in SECTION_NAMES:
            if clean == section:
                found[section] = idx + 1

    return found


def parse_sections_with_llm(region_text: str):
    """
    Returns:
    - extracted_sections: dict(section -> text)
    - debug_map: combined LLM + fallback map
    """

    lines = region_text.splitlines()

    # ---- LLM PASS ----
    prompt = build_section_prompt(region_text)
    llm_output = gemini_llm(prompt)
    llm_map = _parse_llm_output(llm_output)

    # ---- FALLBACK PASS ----
    fallback_map = _regex_fallback_lines(lines)

    # ---- MERGE (LLM wins if present) ----
    merged = {}
    for section in SECTION_NAMES:
        merged[section] = (
            llm_map.get(section)
            if llm_map.get(section) is not None
            else fallback_map.get(section)
        )

    # ---- EXTRACT SECTIONS ----
    extracted = {}

    ordered = sorted(
        [(k, v) for k, v in merged.items() if v],
        key=lambda x: x[1]
    )

    for idx, (section, start_line) in enumerate(ordered):
        start_idx = start_line - 1
        end_idx = (
            ordered[idx + 1][1] - 1
            if idx + 1 < len(ordered)
            else len(lines)
        )

        extracted[section] = "\n".join(
            lines[start_idx:end_idx]
        ).strip()

    return extracted, merged
