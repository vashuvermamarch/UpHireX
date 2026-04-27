"""
Resume Service — Handles resume generation and improvement via Opal agents.

- generate_resume()  → calls Resume Generator Agent → returns resume text
- improve_resume()   → calls Resume Improvement Agent → returns corrections
"""
import logging
from .gemini_client import call_gemini_agent

logger = logging.getLogger(__name__)


def generate_resume(payload):
    """
    Call the Resume Generator Agent and return the generated resume text.

    Parameters
    ----------
    payload : dict
        {'message': '...', 'resume': '...', 'job_title': '...'}

    Returns
    -------
    dict
        {'resume_text': '...'} on success
        {'resume_text': '', 'error': '...'} on failure
    """
    result = call_gemini_agent('resume_generate', payload)

    if result.get('success'):
        resume_text = result.get('response', '')
        logger.info(f"Resume generated: {len(resume_text)} characters")
        return {'resume_text': resume_text}

    error_msg = result.get('error', 'Failed to generate resume')
    logger.error(f"Resume generation failed: {error_msg}")
    return {'resume_text': '', 'error': error_msg}


def improve_resume(payload):
    """
    Call the Resume Improvement Agent and return corrections / suggestions.

    Parameters
    ----------
    payload : dict
        {'message': '...', 'resume': '...', 'job_title': '...'}

    Returns
    -------
    dict
        {'corrections': ['...', '...']} on success
        {'corrections': [], 'error': '...'} on failure
    """
    if not payload.get('resume'):
        return {
            'corrections': [],
            'error': 'Please provide your existing resume text for review.',
        }

    result = call_gemini_agent('resume_improve', payload)

    if result.get('success'):
        response_text = result.get('response', '')
        # Split the response into individual corrections/suggestions
        corrections = _parse_corrections(response_text)
        logger.info(f"Resume improvement: {len(corrections)} corrections found")
        return {'corrections': corrections}

    error_msg = result.get('error', 'Failed to review resume')
    logger.error(f"Resume improvement failed: {error_msg}")
    return {'corrections': [], 'error': error_msg}


def _parse_corrections(text):
    """
    Parse the agent's raw text response into a list of correction strings.
    The agent may return bullet points, numbered lists, or free-form text.
    """
    if not text:
        return []

    lines = text.strip().split('\n')
    corrections = []

    for line in lines:
        cleaned = line.strip()
        # Skip empty lines
        if not cleaned:
            continue
        # Remove common list prefixes (-, *, 1., 2., etc.)
        cleaned = cleaned.lstrip('-*•').strip()
        if cleaned and len(cleaned) > 2:
            # Remove leading numbering like "1. ", "2) "
            import re
            cleaned = re.sub(r'^\d+[\.\)]\s*', '', cleaned).strip()
            if cleaned:
                corrections.append(cleaned)

    # If no structured corrections found, return the entire text as one item
    if not corrections and text.strip():
        corrections = [text.strip()]

    return corrections
