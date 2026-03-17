import uuid
from django.db import models
from django.conf import settings


class FileUpload(models.Model):
    """File upload per schema. Generic via entity_id/entity_type."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='file_uploads',
    )
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True, default='')
    entity_id = models.CharField(max_length=255, blank=True, default='')
    entity_type = models.CharField(max_length=100, blank=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'file_uploads'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['entity_id', 'entity_type']),
        ]

    def __str__(self):
        return f"{self.file_name} by {self.user.username}"
