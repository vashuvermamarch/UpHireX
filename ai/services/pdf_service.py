"""
PDF Service — Convert AI-generated Markdown into a professional A4 resume PDF.

Pipeline:
Markdown → HTML → Styled A4 HTML → WeasyPrint → Multi-page PDF → BytesIO

Requirements:
- markdown
- weasyprint
"""
import logging
import io

logger = logging.getLogger(__name__)

try:
    import markdown
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"WeasyPrint or Markdown not available: {e}. PDF generation will fail.")
    WEASYPRINT_AVAILABLE = False
except Exception as e:
    logger.warning(f"System libraries for WeasyPrint missing: {e}. PDF generation will fail.")
    WEASYPRINT_AVAILABLE = False

from django.conf import settings

# ── RESUME CSS TEMPLATE ──────────────────────────────────
RESUME_CSS = """
@page {
    size: A4;
    margin: 0.75in 0.8in 0.75in 0.8in;
}

body {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #222;
    margin: 0;
    padding: 0;
}

/* Typography & Layout */
h1 {
    font-size: 22pt;
    font-weight: bold;
    text-align: center;
    margin-bottom: 8px;
    margin-top: 0;
}

.contact-info {
    font-size: 10.5pt;
    text-align: center;
    margin-bottom: 18px;
}

h2 {
    font-size: 13pt;
    font-weight: bold;
    text-transform: uppercase;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4px;
    margin-top: 18px;
    margin-bottom: 10px;
}

h3 {
    font-size: 11.5pt;
    font-weight: bold;
    margin-top: 12px;
    margin-bottom: 6px;
}

p {
    margin-bottom: 8px;
}

ul {
    margin-left: 18px;
    margin-bottom: 10px;
    padding-left: 0;
}

li {
    margin-bottom: 6px;
    line-height: 1.5;
    page-break-inside: avoid;
}

/* Natural Pagination */
h2, h3 {
    page-break-after: avoid;
}

.section-block {
    page-break-inside: avoid;
    margin-bottom: 15px;
}

/* ATS Safety: No tables, no columns, just clean semantic layout */
"""

def generate_resume_pdf_buffer(resume_text):
    """
    Convert Markdown string to a PDF byte stream.
    """
    if not WEASYPRINT_AVAILABLE:
        logger.error("PDF generation attempted but WeasyPrint/Markdown is not correctly installed.")
        return None

    try:
        # 1. Convert Markdown to HTML
        html_content = markdown.markdown(resume_text, extensions=['extra', 'smarty'])

        # 2. Wrap Sections for better pagination
        # We wrap each H2 and everything following it until the next H2 in a section-block.
        import re
        
        # Add section blocks to prevent breaks between header and content
        sections = re.split(r'(?=<h2)', html_content)
        processed_html = ""
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            if i == 0:
                # This is the header part (H1 and contact info)
                # Apply contact-info class to the first paragraph after H1
                header_part = re.sub(r'(</h1>\s*<p>)', r'\1', section) # placeholder for more complex logic
                if '</h1>' in header_part:
                    parts = header_part.split('</h1>', 1)
                    name_part = parts[0] + '</h1>'
                    rest = parts[1].strip()
                    if rest.startswith('<p>'):
                        rest = rest.replace('<p>', '<p class="contact-info">', 1)
                    header_part = name_part + rest
                processed_html += header_part
            else:
                # This is a section starting with H2
                processed_html += f'<div class="section-block">{section}</div>'

        # 3. Final HTML Assembly
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>{RESUME_CSS}</style>
        </head>
        <body>
            {processed_html}
        </body>
        </html>
        """

        # 4. Generate PDF using WeasyPrint
        pdf_buffer = io.BytesIO()
        HTML(string=full_html).write_pdf(pdf_buffer)
        
        pdf_buffer.seek(0)
        return pdf_buffer

    except Exception as e:
        logger.error(f"WeasyPrint PDF generation failed: {e}")
        return None

def generate_resume_pdf(resume_text, user_id):
    """
    Legacy wrapper for compatibility with existing views if needed,
    but preferred usage is generate_resume_pdf_buffer.
    """
    # This now returns a buffer-based response-like dict
    buffer = generate_resume_pdf_buffer(resume_text)
    if buffer:
        return {'buffer': buffer, 'filename': f"resume_{user_id}.pdf"}
    return {'error': 'Failed to generate PDF'}
