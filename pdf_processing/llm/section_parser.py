from pdf_processing.llm.prompts import build_section_prompt

def parse_sections_with_llm(region, region_text, llm_client):
    lines = region_text.splitlines()

    numbered = "\n".join(
        f"{i+1}: {line}" for i, line in enumerate(lines)
    )

    prompt = build_section_prompt(region, numbered)
    result = llm_client(prompt)

    return result["sections"], lines
