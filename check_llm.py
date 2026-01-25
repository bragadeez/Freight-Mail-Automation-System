from pdf_processing.llm.section_parser import parse_sections_with_llm

sample_text = """
SUMMARY
This week shows moderate improvement.

OCEAN FREIGHT
Rates are stable across APAC.

AIR FREIGHT
Demand remains steady.

ADVISORY
Book early.
"""

sections, line_map = parse_sections_with_llm(sample_text)

print("=== LINE MAP ===")
print(line_map)

print("\n=== SECTIONS ===")
for k, v in sections.items():
    print(f"\n--- {k} ---")
    print(v)
