def build_section_prompt(region: str, numbered_text: str) -> str:
    return f"""
You are a parser, not a writer.

Task:
Given the freight market report text for the region "{region}",
identify the starting LINE NUMBER for each section.

Allowed sections (exact names only):
- SUMMARY
- OCEAN FREIGHT
- AIR FREIGHT
- MULTIMODAL
- POLITICAL & REGULATORY
- CLIMATE & WEATHER
- ADVISORY

Rules:
- Do NOT rewrite text
- Do NOT summarize
- Do NOT invent sections
- If a section is missing, return null
- Return ONLY valid JSON
- No explanations

Return format:
{{
  "sections": {{
    "SUMMARY": <line_or_null>,
    "OCEAN FREIGHT": <line_or_null>,
    "AIR FREIGHT": <line_or_null>,
    "MULTIMODAL": <line_or_null>,
    "POLITICAL & REGULATORY": <line_or_null>,
    "CLIMATE & WEATHER": <line_or_null>,
    "ADVISORY": <line_or_null>
  }}
}}

Output format MUST be application/json.
Return only a single JSON object.

TEXT:
{numbered_text}
"""
