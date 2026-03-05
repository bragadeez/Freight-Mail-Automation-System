import os

def get_latest_pdf(directory):
    pdfs = [
        f for f in os.listdir(directory)
        if f.lower().endswith(".pdf")
    ]

    if not pdfs:
        raise FileNotFoundError("No PDF found in input directory")

    pdfs.sort(
        key=lambda f: os.path.getmtime(os.path.join(directory, f)),
        reverse=True
    )

    return os.path.join(directory, pdfs[0])

def get_latest_docx(directory):
    docxs = [
        f for f in os.listdir(directory)
        if f.lower().endswith(".docx")
    ]

    if not docxs:
        raise FileNotFoundError("No DOCX found in input directory")

    docxs.sort(
        key=lambda f: os.path.getmtime(os.path.join(directory, f)),
        reverse=True
    )

    return os.path.join(directory, docxs[0])