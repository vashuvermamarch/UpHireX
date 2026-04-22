"""
PDF Service — Convert resume plain text into a beautifully formatted PDF.

Uses WeasyPrint to render an HTML template → PDF.
Saved to: media/resumes/resume_<user_id>_<timestamp>.pdf
Always generates a NEW file; never reuses old files.
"""
import logging
import os
import uuid
from datetime import datetime

from django.conf import settings
from weasyprint import HTML

logger = logging.getLogger(__name__)

# ── Output directory ────────────────────────────────────
RESUME_DIR = os.path.join(settings.MEDIA_ROOT, 'resumes')


def generate_resume_pdf(resume_text, user_id):
    """
    Convert resume_text → HTML → PDF and save to disk.

    Parameters
    ----------
    resume_text : str   – plain / markdown-ish text from the AI agent
    user_id     : str   – UUID of the authenticated user

    Returns
    -------
    dict
        {'pdf_url': '/media/resumes/resume_xxx.pdf', 'pdf_path': '...'}
        or {'pdf_url': '', 'error': '...'} on failure
    """
    if not resume_text:
        return {'pdf_url': '', 'error': 'No resume text provided.'}

    try:
        os.makedirs(RESUME_DIR, exist_ok=True)

        # Unique filename (never reuse)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        short_id = str(uuid.uuid4())[:8]
        filename = f"resume_{user_id}_{timestamp}_{short_id}.pdf"
        pdf_path = os.path.join(RESUME_DIR, filename)

        # Build HTML from resume text
        html_content = _build_resume_html(resume_text)

        # Render to PDF
        HTML(string=html_content).write_pdf(pdf_path)

        # Relative URL for the API response
        pdf_url = f"{settings.MEDIA_URL}resumes/{filename}"

        logger.info(f"PDF generated: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
        return {'pdf_url': pdf_url, 'pdf_path': pdf_path}

    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return {'pdf_url': '', 'error': str(e)}


def _build_resume_html(resume_text):
    """
    Convert resume plain text into clean, professionally styled HTML.
    Handles markdown-like headers (##, **bold**) and bullet points.
    """
    import re

    # Escape HTML special characters
    escaped = (
        resume_text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
    )

    lines = escaped.split('\n')
    html_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            html_lines.append('<br/>')
            continue

        # Markdown-style headers
        if stripped.startswith('### '):
            html_lines.append(f'<h3>{stripped[4:]}</h3>')
        elif stripped.startswith('## '):
            html_lines.append(f'<h2>{stripped[3:]}</h2>')
        elif stripped.startswith('# '):
            html_lines.append(f'<h1>{stripped[2:]}</h1>')
        # Bullet points
        elif stripped.startswith('- ') or stripped.startswith('* ') or stripped.startswith('• '):
            html_lines.append(f'<li>{stripped[2:]}</li>')
        else:
            html_lines.append(f'<p>{stripped}</p>')

    body = '\n'.join(html_lines)

    # Wrap <li> groups in <ul>
    body = re.sub(r'((?:<li>.*?</li>\n?)+)', r'<ul>\1</ul>', body)

    # Handle **bold** markers
    body = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', body)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <style>
        @page {{
            size: A4;
            margin: 2cm 2.5cm;
        }}
        body {{
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #1a1a1a;
            margin: 0;
            padding: 0;
        }}
        h1 {{
            font-size: 22pt;
            color: #0d1b2a;
            margin-bottom: 4px;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 6px;
        }}
        h2 {{
            font-size: 14pt;
            color: #1e3a5f;
            margin-top: 18px;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 3px;
        }}
        h3 {{
            font-size: 12pt;
            color: #334155;
            margin-top: 12px;
            margin-bottom: 4px;
        }}
        p {{
            margin: 4px 0;
        }}
        ul {{
            margin: 4px 0 8px 0;
            padding-left: 20px;
        }}
        li {{
            margin: 2px 0;
        }}
        strong {{
            color: #0f172a;
        }}
        br {{
            display: block;
            margin: 4px 0;
            content: "";
        }}
    </style>
</head>
<body>
{body}
</body>
</html>"""
