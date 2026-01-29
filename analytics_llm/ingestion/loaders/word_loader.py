import docx


def load_word(file) -> dict:
    document = docx.Document(file)
    text = "\n".join([p.text for p in document.paragraphs])
    return {"type": "document", "text": text}
