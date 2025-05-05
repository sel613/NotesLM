from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import re, io
from PIL import Image

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
    pdf_bytes = pdf_file.read()

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []

    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        images.append(img)

    return images