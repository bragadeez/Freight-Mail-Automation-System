from pdf_processing.llm.gemini_client import gemini_llm
from pdf_processing.llm.section_parser import parse_sections_with_llm

with open("sample_region.txt", "r", encoding="utf-8") as f:
    text = f.read()

sections, _ = parse_sections_with_llm(
    "GCC",
    text,
    gemini_llm
)

print(sections)
