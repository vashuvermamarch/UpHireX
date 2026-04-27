import PyPDF2
import io
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_obj):
    """
    Extracts text from a PDF file object.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(file_obj)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""
