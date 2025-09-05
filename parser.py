import fitz 
import pytesseract
from pdf2image import convert_from_path
from pathlib import Path

def extract_text_with_ocr(pdf_path: str | Path, lang: str = "por") -> str:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text_output = []

    # Open with PyMuPDF
    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if text.strip():
            # Page already has selectable text
            text_output.append(text)
        else:
            # No text -> likely scanned image, do OCR
            images = convert_from_path(
                str(pdf_path), dpi=300, first_page=page_num, last_page=page_num
            )
            for img in images:
                ocr_text = pytesseract.image_to_string(img, lang=lang)
                text_output.append(ocr_text)

    doc.close()
    return "\n".join(text_output)



