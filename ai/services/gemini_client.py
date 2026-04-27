import logging
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Configure the Gemini SDK
GEMINI_API_KEY = getattr(settings, 'GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in settings.")

# System Instructions for different agents
SYSTEM_INSTRUCTIONS = {
    'resume_generate': (
        "You are an expert Resume Writer. "
        "Your goal is to create a professional, ATS-optimized resume. "
        "IMPORTANT: Output ONLY the resume content itself. "
        "DO NOT include any introductory sentences, meta-talk, or descriptions like 'This is a professional resume...'. "
        "Start directly with the Name/Header. "
        "Focus on quantifiable achievements and strong action verbs."
    ),
    'resume_improve': (
        "You are an expert Resume Reviewer. "
        "Analyze the provided resume and suggest specific, actionable improvements. "
        "Focus on clarity, impact, formatting, and keyword optimization. "
        "Provide your suggestions as a concise list of bullet points."
    ),
    'career_chat': (
        "You are Synora, a friendly and professional Career Assistant. "
        "Provide helpful advice on career growth, interview preparation, networking, and job searching. "
        "Keep your responses encouraging, concise, and practical."
    ),
}

def call_gemini_agent(agent_key, payload):
    """
    Unified call to Gemini models with specific system instructions.
    
    Parameters
    ----------
    agent_key : str
        One of 'resume_generate', 'resume_improve', 'career_chat'.
    payload : dict
        {'message': '...', 'resume': '...', 'job_title': '...'}
        
    Returns
    -------
    dict
        {'success': True, 'response': '...'} or {'success': False, 'error': '...'}
    """
    if not GEMINI_API_KEY:
        return {'success': False, 'error': 'Gemini API Key is missing.'}

    instruction = SYSTEM_INSTRUCTIONS.get(agent_key)
    if not instruction:
        return {'success': False, 'error': f'Unknown agent key: {agent_key}'}

    try:
        model = genai.GenerativeModel(
            model_name="gemini-3-flash-preview",
            system_instruction=instruction
        )

        # Construct the prompt
        prompt_parts = []
        if payload.get('job_title'):
            prompt_parts.append(f"Target Job Title: {payload['job_title']}")
        if payload.get('resume'):
            prompt_parts.append(f"Existing Resume:\n{payload['resume']}")
        if payload.get('message'):
            prompt_parts.append(f"User Request: {payload['message']}")
        
        prompt = "\n\n".join(prompt_parts)

        logger.info(f"Calling Gemini agent '{agent_key}'")
        response = model.generate_content(prompt)

        if response and response.text:
            return {'success': True, 'response': response.text}
        
        return {'success': False, 'error': 'Empty response from Gemini.'}

    except Exception as e:
        logger.error(f"Error calling Gemini agent '{agent_key}': {str(e)}")
        return {'success': False, 'error': str(e)}
