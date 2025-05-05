from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import re
# Replace this with an actual path to a known working PDF
pdf_path = rf"C:\Users\selva\Downloads\Course 1.pdf"

# images = convert_from_path(pdf_path)
# print(f"Converted {len(images)} pages.")
# images[0].show()  # Opens first page as image


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
print(extract_text_from_pdf(pdf_path))