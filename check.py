from pdf_processing.layout_extractor import extract_layout_blocks

blocks = extract_layout_blocks("data/input_pdfs/Week46.pdf")

for b in blocks[:30]:
    print(b)