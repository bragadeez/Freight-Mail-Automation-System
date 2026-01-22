from pdf_processing.llm.schema import validate_llm_output
from pdf_processing.llm.section_extractor import extract_sections_from_lines

def parse_region_with_llm_or_fallback(
    region,
    region_text,
    region_blocks,
    llm_parser
):
    try:
        sections, lines = llm_parser(region, region_text)
        validate_llm_output({"sections": sections}, len(lines))
        return extract_sections_from_lines(sections, lines)
    except Exception as e:
        print(f"[LLM FALLBACK] {region}: {e}")
        return {"RAW_BLOCKS": region_blocks}
