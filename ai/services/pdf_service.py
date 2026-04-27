"""
PDF Service — Convert resume plain text into a beautifully formatted PDF.

Uses fpdf2 (Pure Python) to generate PDFs.
Saved to: media/resumes/resume_<user_id>_<timestamp>.pdf
Always generates a NEW file; never reuses old files.
"""
import logging
import os
import uuid
from datetime import datetime
from fpdf import FPDF

from django.conf import settings

logger = logging.getLogger(__name__)

# ── Output directory ────────────────────────────────────
RESUME_DIR = os.path.join(settings.MEDIA_ROOT, 'resumes')


class ResumePDF(FPDF):
    def header(self):
        pass

    def footer(self):
        # Page numbering removed as requested
        pass


def generate_resume_pdf(resume_text, user_id):
    """
    Convert resume_text → PDF and save to disk using fpdf2.
    """
    if not resume_text:
        return {'pdf_url': '', 'error': 'No resume text provided.'}

    try:
        os.makedirs(RESUME_DIR, exist_ok=True)

        # Unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        short_id = str(uuid.uuid4())[:8]
        filename = f"resume_{user_id}_{timestamp}_{short_id}.pdf"
        pdf_path = os.path.join(RESUME_DIR, filename)

        # Create PDF object
        pdf = ResumePDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Calculate usable width safely
        usable_width = 210 - pdf.l_margin - pdf.r_margin - 2 # 2mm extra safety buffer
        
        # Sanitize text for Latin-1 compatibility
        sanitized_text = resume_text.encode('latin-1', 'replace').decode('latin-1')
        lines = sanitized_text.split('\n')
        
        for line in lines:
            try:
                line = line.strip()
                pdf.set_x(pdf.l_margin) # Reset to left margin for every line
                
                if not line:
                    pdf.ln(5)
                    continue
                
                # Heading 1 (Title)
                if line.startswith('# '):
                    pdf.set_font("helvetica", "B", 20)
                    pdf.set_text_color(13, 27, 42)
                    pdf.multi_cell(usable_width, 12, line[2:], align='L')
                    pdf.ln(2)
                    pdf.set_text_color(0, 0, 0)
                
                # Heading 2 (Sections)
                elif line.startswith('## '):
                    pdf.set_font("helvetica", "B", 14)
                    pdf.set_text_color(30, 58, 95)
                    pdf.multi_cell(usable_width, 10, line[3:].upper(), align='L')
                    # Draw a horizontal line
                    curr_y = pdf.get_y()
                    pdf.line(pdf.l_margin, curr_y, 210 - pdf.r_margin, curr_y)
                    pdf.ln(2)
                    pdf.set_text_color(0, 0, 0)
                
                # Heading 3 (Sub-sections)
                elif line.startswith('### '):
                    pdf.set_font("helvetica", "B", 12)
                    pdf.set_text_color(50, 50, 50)
                    pdf.multi_cell(usable_width, 8, line[4:], align='L')
                    pdf.set_font("helvetica", "", 11)
                    pdf.set_text_color(0, 0, 0)

                # Bullet points
                elif line.startswith('- ') or line.startswith('* '):
                    pdf.set_font("helvetica", "", 11)
                    # Use fpdf2 markdown support for bold markers within bullets
                    pdf.multi_cell(usable_width, 6, f"- {line[2:]}", markdown=True)
                
                # Horizontal rule
                elif line.startswith('---') or line.startswith('***'):
                    pdf.ln(2)
                    curr_y = pdf.get_y()
                    pdf.line(pdf.l_margin, curr_y, 210 - pdf.r_margin, curr_y)
                    pdf.ln(2)

                # Normal text
                else:
                    pdf.set_font("helvetica", "", 11)
                    # Use markdown=True to handle **bold** automatically
                    pdf.multi_cell(usable_width, 6, line, markdown=True)
            except Exception as line_err:
                logger.warning(f"Skipping PDF line due to error: {line_err}")
                continue

        # Save PDF
        pdf.output(pdf_path)

        # Relative URL for response
        pdf_url = f"{settings.MEDIA_URL}resumes/{filename}"

        logger.info(f"PDF generated using fpdf2: {pdf_path}")
        return {'pdf_url': pdf_url, 'pdf_path': pdf_path}

    except Exception as e:
        logger.error(f"fpdf2 generation failed: {e}")
        return {'pdf_url': '', 'error': str(e)}
