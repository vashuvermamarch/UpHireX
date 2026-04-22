"""
AI Assistant Views — Single unified endpoint.

POST /api/v1/ai/assistant/

Accepts user input, detects intent, routes to the correct Opal agent,
generates PDF if needed, stores conversation in the chat system, and
returns a structured response.
"""
import logging

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from uphirex.utils import api_response
from authapp.decorators import IsJobSeeker

from .services.router import route_request
from .services.pdf_service import generate_resume_pdf

from chat.models import ChatRoom, ChatParticipant, Message

logger = logging.getLogger(__name__)

# Name for the AI assistant chat room
AI_ROOM_NAME = 'Uphirex AI Assistant'


class AIAssistantView(APIView):
    """
    POST /api/v1/ai/assistant/

    Body:
        {
            "message":   "Create a resume for a backend developer",
            "resume":    "... existing resume text (optional) ...",
            "job_title": "Backend Developer (optional)"
        }

    Response:
        {
            "intent":       "resume_generate",
            "message":      "Resume generated successfully.",
            "corrections":  [],
            "resume_text":  "...",
            "pdf_url":      "/media/resumes/resume_xxx.pdf",
            "pdf_required": true
        }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get('message', '').strip()
        resume = request.data.get('resume', '').strip()
        job_title = request.data.get('job_title', '').strip()

        if not message:
            return api_response(
                False, 'Message is required.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # ── RBAC: resume features restricted to job_seeker ──
        # (career_chat is open to all authenticated users)
        from .services.router import detect_intent
        intent = detect_intent(message)

        if intent in ('resume_generate', 'resume_improve'):
            if request.user.role not in ('job_seeker', 'admin'):
                return api_response(
                    False,
                    'Resume features are available to job seekers only.',
                    status_code=status.HTTP_403_FORBIDDEN,
                )

        # ── Route to the correct agent ──────────────────────
        result = route_request(message, resume=resume, job_title=job_title)

        # ── Generate PDF for resume_generate ────────────────
        pdf_url = ''
        if result.get('pdf_required') and result.get('resume_text'):
            pdf_result = generate_resume_pdf(
                result['resume_text'], str(request.user.id),
            )
            pdf_url = pdf_result.get('pdf_url', '')

        # ── Store in chat memory ────────────────────────────
        self._store_conversation(
            user=request.user,
            user_message=message,
            ai_response=result.get('message') or result.get('resume_text', ''),
            intent=intent,
            resume=resume,
            job_title=job_title,
        )

        # ── Build unified response ──────────────────────────
        response_data = {
            'intent': result.get('intent', intent),
            'message': result.get('message', ''),
            'corrections': result.get('corrections', []),
            'resume_text': result.get('resume_text', ''),
            'pdf_url': pdf_url,
            'pdf_required': result.get('pdf_required', False),
        }

        return api_response(True, 'AI response ready.', response_data, status.HTTP_200_OK)

    def _store_conversation(self, user, user_message, ai_response, intent, resume, job_title):
        """
        Save the conversation turn in the existing chat system.
        Uses a dedicated AI Assistant chat room per user.
        """
        try:
            # Get or create the user's AI chat room
            room = ChatRoom.objects.filter(
                name=AI_ROOM_NAME,
                type='direct',
                participants__user=user,
            ).first()

            if not room:
                room = ChatRoom.objects.create(name=AI_ROOM_NAME, type='direct')
                ChatParticipant.objects.create(room=room, user=user)

            # Store user message with metadata
            metadata = f"[intent={intent}]"
            if job_title:
                metadata += f" [job_title={job_title}]"

            Message.objects.create(
                room=room,
                sender=user,
                content=f"{metadata}\n{user_message}",
                message_type='text',
            )

            # Store AI response
            Message.objects.create(
                room=room,
                sender=user,  # system message tagged as AI
                content=f"[AI_RESPONSE] [intent={intent}]\n{ai_response[:2000]}",
                message_type='system',
            )

            from django.utils import timezone
            room.last_message_at = timezone.now()
            room.save(update_fields=['last_message_at'])

        except Exception as e:
            logger.error(f"Failed to store AI conversation: {e}")
