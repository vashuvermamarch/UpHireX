"""
Opal Client — HTTP interface to Google Opal AI agents.

Each Opal app exposes an internal API via appcatalyst.pa.googleapis.com.
This client wraps those calls with timeout, retry, and error-handling logic.

NOTE: Opal is an experimental Google Labs platform.  The internal API is
NOT officially documented.  If it becomes unavailable, the client will
return a graceful error that the service layer can handle (e.g. by
falling back to a local Gemini SDK call in the future).
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# ── Agent configuration ─────────────────────────────────
OPAL_AGENTS = {
    'resume_generate': {
        'app_id': '13ObAXcIdra4tg_pzjVl3btzSJyCTirZq',
        'url': 'https://opal.google/app/13ObAXcIdra4tg_pzjVl3btzSJyCTirZq',
        'description': 'Resume Generator Agent – creates ATS-optimized resumes',
    },
    'resume_improve': {
        'app_id': '1b1NZE8CetMqYYqS3rWxP7kK5SAmXEZWp',
        'url': 'https://opal.google/app/1b1NZE8CetMqYYqS3rWxP7kK5SAmXEZWp',
        'description': 'Resume Improvement Agent – corrections and suggestions',
    },
    'career_chat': {
        'app_id': '19V6lc6pQbqSN-ojFHvR6F2SpDwWYUGP0',
        'url': 'https://opal.google/app/19V6lc6pQbqSN-ojFHvR6F2SpDwWYUGP0',
        'description': 'Career Chatbot Agent – general career queries',
    },
}

OPAL_BACKEND_API = 'https://appcatalyst.pa.googleapis.com'
REQUEST_TIMEOUT = 30  # seconds


def call_opal_agent(agent_key, payload):
    """
    Send a message to an Opal agent and return the text response.

    Parameters
    ----------
    agent_key : str
        One of 'resume_generate', 'resume_improve', 'career_chat'.
    payload : dict
        Must contain at least 'message'.  Optionally 'resume', 'job_title'.

    Returns
    -------
    dict
        {'success': True, 'response': '<agent text>'} on success.
        {'success': False, 'error': '<description>'} on failure.
    """
    agent = OPAL_AGENTS.get(agent_key)
    if not agent:
        return {'success': False, 'error': f'Unknown agent key: {agent_key}'}

    opal_api_key = getattr(settings, 'OPAL_API_KEY', '')

    # Build the request to the Opal backend
    try:
        # Construct the message for the agent
        message_parts = []
        if payload.get('message'):
            message_parts.append(payload['message'])
        if payload.get('job_title'):
            message_parts.append(f"Job Title: {payload['job_title']}")
        if payload.get('resume'):
            message_parts.append(f"Resume:\n{payload['resume']}")

        full_message = '\n\n'.join(message_parts)

        # Opal AppCatalyst API endpoint
        url = f"{OPAL_BACKEND_API}/v1/apps/{agent['app_id']}:run"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        # Add API key if configured
        if opal_api_key:
            headers['Authorization'] = f'Bearer {opal_api_key}'

        request_body = {
            'input': {
                'message': full_message,
            },
        }

        logger.info(f"Calling Opal agent '{agent_key}' ({agent['app_id']})")

        resp = requests.post(
            url,
            json=request_body,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )

        if resp.status_code == 200:
            data = resp.json()
            # Extract agent text from response
            response_text = (
                data.get('output', {}).get('message', '')
                or data.get('output', {}).get('text', '')
                or data.get('result', {}).get('output', '')
                or data.get('response', '')
                or str(data)
            )
            return {'success': True, 'response': response_text}

        # Non-200 status – log and return error
        logger.warning(
            f"Opal agent '{agent_key}' returned {resp.status_code}: "
            f"{resp.text[:300]}"
        )
        return {
            'success': False,
            'error': f'Opal agent returned status {resp.status_code}',
            'status_code': resp.status_code,
        }

    except requests.exceptions.Timeout:
        logger.error(f"Opal agent '{agent_key}' timed out after {REQUEST_TIMEOUT}s")
        return {'success': False, 'error': 'Agent request timed out'}

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error calling Opal agent '{agent_key}': {e}")
        return {'success': False, 'error': 'Unable to reach Opal agent'}

    except Exception as e:
        logger.error(f"Unexpected error calling Opal agent '{agent_key}': {e}")
        return {'success': False, 'error': str(e)}
