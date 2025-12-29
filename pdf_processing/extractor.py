import pdfplumber
import fitz  # PyMuPDF
import json
import os

def extract_text_exact(pdf_path, output_path):
    extracted = {
        "pages": {}
    }

    # First try pdfplumber (better for tables & bullets)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                extracted["pages"][str(i + 1)] = text or ""
    except Exception:
        # Fallback to PyMuPDF
        doc = fitz.open(pdf_path)
        for i in range(len(doc)):
            page = doc[i]
            extracted["pages"][str(i + 1)] = page.get_text()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)

    return extracted
