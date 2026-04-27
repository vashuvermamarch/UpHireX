"""
Chatbot Service — General career chatbot via Opal Career Chatbot Agent.
"""
import logging
from .gemini_client import call_gemini_agent

logger = logging.getLogger(__name__)


def career_chat(payload):
    """
    Call the Career Chatbot Agent and return the reply.

    Parameters
    ----------
    payload : dict
        {'message': '...', 'resume': '...', 'job_title': '...'}

    Returns
    -------
    dict
        {'message': 'AI reply ...'} on success
        {'message': 'Sorry, ...', 'error': '...'} on failure
    """
    result = call_gemini_agent('career_chat', payload)

    if result.get('success'):
        message = result.get('response', '')
        logger.info(f"Career chat reply: {len(message)} characters")
        return {'message': message}

    error_msg = result.get('error', 'Failed to get career advice')
    logger.error(f"Career chat failed: {error_msg}")
    return {
        'message': 'Sorry, I could not process your request right now. Please try again.',
        'error': error_msg,
    }
