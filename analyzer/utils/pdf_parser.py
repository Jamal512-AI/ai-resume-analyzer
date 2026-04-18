"""
PDF, DOCX and TXT text extraction utilities.
"""
from PyPDF2 import PdfReader


def extract_text_from_pdf(file):
    """Extract text from an uploaded PDF file."""
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(file):
    """Extract text from an uploaded DOCX file."""
    try:
        from docx import Document
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text.strip()
    except ImportError:
        raise ImportError("python-docx is required for DOCX support. Install it with: pip install python-docx")


def extract_text_from_txt(file):
    """Extract text from an uploaded TXT file."""
    content = file.read()
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    return content.strip()


def extract_text(file, filename):
    """
    Router: extract text from any supported file format.
    Supports .pdf, .docx, .txt
    """
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''

    if ext == 'pdf':
        return extract_text_from_pdf(file)
    elif ext == 'docx':
        return extract_text_from_docx(file)
    elif ext == 'txt':
        return extract_text_from_txt(file)
    else:
        raise ValueError(f"Unsupported file format: .{ext}. Please upload a PDF, DOCX, or TXT file.")
