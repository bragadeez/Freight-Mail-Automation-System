def build_section_prompt(region_text: str) -> str:
    """
    Build a deterministic prompt for Gemini.
    We ask ONLY for section start line numbers.
    """

    lines = region_text.splitlines()

    numbered_text = "\n".join(
        f"{i+1}: {line}" for i, line in enumerate(lines)
    )

    return f"""
You are given a freight market report section with line numbers.

Your task:
Identify the FIRST line number where each section STARTS.

Sections to detect:
SUMMARY
OCEAN FREIGHT
AIR FREIGHT
MULTIMODAL
POLITICAL & REGULATORY
CLIMATE & WEATHER
ADVISORY

Rules:
- Output EXACTLY one line per section
- Use this format ONLY:
  <SECTION NAME>: <LINE NUMBER or NONE>
- Use NONE if the section is not present
- DO NOT return JSON
- DO NOT explain anything
- DO NOT add extra text

Text:
{numbered_text}
""".strip()
