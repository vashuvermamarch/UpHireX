from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from uphirex.utils import api_response
from .models import ChatRoom, ChatParticipant, Message, MessageRead
from .serializers import ChatRoomSerializer, ChatParticipantSerializer, MessageSerializer, MessageReadSerializer


class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(
            participants__user=self.request.user
        ).distinct().order_by('-last_message_at')

    def create(self, request, *args, **kwargs):
        """Create a chat room and add participants."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()

        # Add creator as participant
        ChatParticipant.objects.create(room=room, user=request.user)

        # Add other participants
        participant_ids = request.data.get('participant_ids', [])
        for pid in participant_ids:
            ChatParticipant.objects.get_or_create(room=room, user_id=pid)

        return api_response(True, "Chat room created.", ChatRoomSerializer(room).data, status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a room."""
        room = self.get_object()
        if not ChatParticipant.objects.filter(room=room, user=request.user).exists():
            return api_response(False, "Not a participant.", status_code=status.HTTP_403_FORBIDDEN)
        messages = Message.objects.filter(room=room, deleted_at__isnull=True).select_related('sender')[:100]
        return api_response(True, "Messages.", MessageSerializer(messages, many=True).data, status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to a room."""
        room = self.get_object()
        if not ChatParticipant.objects.filter(room=room, user=request.user).exists():
            return api_response(False, "Not a participant.", status_code=status.HTTP_403_FORBIDDEN)

        msg = Message.objects.create(
            room=room, sender=request.user,
            content=request.data.get('content', ''),
            message_type=request.data.get('message_type', 'text'),
            file_url=request.data.get('file_url', ''),
        )
        room.last_message_at = timezone.now()
        room.save(update_fields=['last_message_at'])

        return api_response(True, "Message sent.", MessageSerializer(msg).data, status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark messages as read."""
        room = self.get_object()
        message_ids = request.data.get('message_ids', [])
        for mid in message_ids:
            MessageRead.objects.get_or_create(message_id=mid, user=request.user)

        # Update last_seen
        ChatParticipant.objects.filter(room=room, user=request.user).update(last_seen=timezone.now())
        return api_response(True, "Messages marked as read.", status_code=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        room = self.get_object()
        ps = ChatParticipant.objects.filter(room=room).select_related('user')
        return api_response(True, "Participants.", ChatParticipantSerializer(ps, many=True).data, status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def direct(self, request):
        """Get or create a direct chat with another user."""
        other_user_id = request.data.get('user_id')
        if str(request.user.id) == str(other_user_id):
            return api_response(False, "Cannot chat with yourself.", status_code=status.HTTP_400_BAD_REQUEST)

        # Check for existing direct room
        my_rooms = ChatRoom.objects.filter(type='direct', participants__user=request.user)
        for room in my_rooms:
            if ChatParticipant.objects.filter(room=room, user_id=other_user_id).exists():
                return api_response(True, "Existing chat.", ChatRoomSerializer(room).data, status.HTTP_200_OK)

        # Create new direct room
        room = ChatRoom.objects.create(type='direct')
        ChatParticipant.objects.create(room=room, user=request.user)
        ChatParticipant.objects.create(room=room, user_id=other_user_id)
        return api_response(True, "Direct chat created.", ChatRoomSerializer(room).data, status.HTTP_201_CREATED)
