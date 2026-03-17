import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Notification per schema."""

    class NotificationType(models.TextChoices):
        PROFILE_VIEW = 'profile_view', 'Profile View'
        JOB_APPLIED = 'job_applied', 'Job Applied'
        MESSAGE = 'message', 'Message'
        JOB_UPDATE = 'job_update', 'Job Update'
        CONNECTION_REQUEST = 'connection_request', 'Connection Request'
        APPLICATION_STATUS = 'application_status', 'Application Status'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications',
    )
    type = models.CharField(max_length=30, choices=NotificationType.choices)
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sent_notifications',
    )
    message = models.CharField(max_length=500, blank=True, default='')
    reference_id = models.CharField(max_length=255, blank=True, default='')
    reference_type = models.CharField(max_length=100, blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.type}"
