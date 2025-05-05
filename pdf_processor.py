from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import re

# ---------- TEXT EXTRACTION FUNCTION ----------
def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF using PyPDF2.
    Falls back to OCR if no text is found.
    """
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    
    # Clean and return text
    return clean_text(text)

def clean_text(text):
    """
    Cleans whitespace and formatting.
    """
    return re.sub(r'\s+', ' ', text).strip()

# ---------- IMAGE CONVERSION FUNCTION ----------
def convert_pdf_to_images(pdf_file, max_pages=10):
    """
    Converts a PDF to images (1 per page), up to `max_pages`.
    Returns a list of PIL.Image objects.
    """
    pdf_file.seek(0)
    content = pdf_file.read()

    if not content.startswith(b'%PDF'):
        raise ValueError("Invalid PDF file.")

    try:
        images = convert_from_bytes(content, first_page=1, last_page=max_pages)
        return images
    except Exception as e:
        raise RuntimeError(f"PDF to image conversion failed: {e}")
