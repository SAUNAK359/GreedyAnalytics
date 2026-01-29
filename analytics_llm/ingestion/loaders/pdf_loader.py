import pdfplumber


def load_pdf(file) -> dict:
    text_chunks = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text_chunks.append(page.extract_text() or "")
    return {"type": "document", "text": "\n".join(text_chunks)}
