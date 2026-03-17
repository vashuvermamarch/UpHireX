import uuid
from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    """Chat room per schema."""

    class RoomType(models.TextChoices):
        DIRECT = 'direct', 'Direct'
        GROUP = 'group', 'Group'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, default='')
    type = models.CharField(max_length=10, choices=RoomType.choices, default=RoomType.DIRECT)
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'chat_rooms'

    def __str__(self):
        return self.name or f"Room {self.id}"


class ChatParticipant(models.Model):
    """Chat room participant per schema. Composite key: room + user."""

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='chat_participations',
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    notification_enabled = models.BooleanField(default=True)

    class Meta:
        db_table = 'chat_participants'
        unique_together = ('room', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.room}"


class Message(models.Model):
    """Chat message per schema."""

    class MessageType(models.TextChoices):
        TEXT = 'text', 'Text'
        IMAGE = 'image', 'Image'
        FILE = 'file', 'File'
        SYSTEM = 'system', 'System'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='messages',
    )
    content = models.TextField(blank=True, default='')
    message_type = models.CharField(
        max_length=10, choices=MessageType.choices, default=MessageType.TEXT,
    )
    file_url = models.URLField(max_length=500, blank=True, default='')
    is_edited = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room']),
            models.Index(fields=['sender']),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class MessageRead(models.Model):
    """Message read receipt per schema. Composite key: message + user."""

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reads')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='message_reads',
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message_reads'
        unique_together = ('message', 'user')

    def __str__(self):
        return f"{self.user.username} read {self.message.id}"
