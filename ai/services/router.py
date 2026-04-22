"""
Intent Router — Detect user intent and route to the correct AI service.

This is the CORE LOGIC layer.  Views call this; it calls the services.
No AI prompts live here — all intelligence is in the external Opal agents.
"""
import logging
import re

logger = logging.getLogger(__name__)

# ── Intent keywords (case-insensitive) ──────────────────
RESUME_GENERATE_KEYWORDS = [
    'create resume', 'build resume', 'make resume', 'generate resume',
    'new resume', 'write resume', 'create my resume', 'build my resume',
    'make my resume', 'write my resume', 'draft resume', 'prepare resume',
    'create a resume', 'build a resume', 'make a resume',
]

RESUME_IMPROVE_KEYWORDS = [
    'improve resume', 'review resume', 'fix resume', 'enhance resume',
    'optimize resume', 'check resume', 'update resume', 'correct resume',
    'improve my resume', 'review my resume', 'fix my resume',
    'resume feedback', 'resume suggestions', 'resume tips',
    'critique resume', 'analyze resume', 'proofread resume',
]


def detect_intent(message):
    """
    Analyse the user message and return one of:
        'resume_generate'  — user wants a NEW resume
        'resume_improve'   — user wants corrections / review
        'career_chat'      — anything else (career advice, tips, etc.)

    Parameters
    ----------
    message : str

    Returns
    -------
    str
    """
    if not message:
        return 'career_chat'

    lower_msg = message.lower().strip()

    # Check resume-generate intent first (more specific)
    for keyword in RESUME_GENERATE_KEYWORDS:
        if keyword in lower_msg:
            logger.info(f"Intent detected: resume_generate (matched '{keyword}')")
            return 'resume_generate'

    # Then resume-improve
    for keyword in RESUME_IMPROVE_KEYWORDS:
        if keyword in lower_msg:
            logger.info(f"Intent detected: resume_improve (matched '{keyword}')")
            return 'resume_improve'

    # Default → career chat
    logger.info("Intent detected: career_chat (default)")
    return 'career_chat'


def route_request(message, resume='', job_title=''):
    """
    High-level orchestrator called by the view.

    1. Detect intent
    2. Call the correct service
    3. Return unified response dict

    Parameters
    ----------
    message   : str – user's input text
    resume    : str – existing resume text (optional)
    job_title : str – target job title (optional)

    Returns
    -------
    dict – unified response ready for the view to return
    """
    from .resume_service import generate_resume, improve_resume
    from .chatbot_service import career_chat

    intent = detect_intent(message)

    payload = {
        'message': message,
        'resume': resume,
        'job_title': job_title,
    }

    if intent == 'resume_generate':
        result = generate_resume(payload)
        return {
            'intent': intent,
            'message': 'Resume generated successfully.' if result.get('resume_text') else result.get('error', ''),
            'resume_text': result.get('resume_text', ''),
            'corrections': [],
            'pdf_required': True,
        }

    elif intent == 'resume_improve':
        result = improve_resume(payload)
        return {
            'intent': intent,
            'message': 'Resume reviewed successfully.' if result.get('corrections') else result.get('error', ''),
            'resume_text': '',
            'corrections': result.get('corrections', []),
            'pdf_required': False,
        }

    else:  # career_chat
        result = career_chat(payload)
        return {
            'intent': intent,
            'message': result.get('message', ''),
            'resume_text': '',
            'corrections': [],
            'pdf_required': False,
        }
