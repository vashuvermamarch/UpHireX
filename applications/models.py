import uuid
from django.db import models
from django.conf import settings


class JobApplication(models.Model):
    """Job application per schema."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        REVIEWED = 'reviewed', 'Reviewed'
        SHORTLISTED = 'shortlisted', 'Shortlisted'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='job_applications',
    )
    job = models.ForeignKey(
        'jobs.JobPost', on_delete=models.CASCADE,
        related_name='applications',
    )
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    cover_letter = models.TextField(blank=True, default='')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_applications'
        unique_together = ('user', 'job')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['job']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.job.title}"


class ApplicationReview(models.Model):
    """Application review per schema."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE,
        related_name='reviews',
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='application_reviews',
    )
    note = models.TextField(blank=True, default='')
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'application_reviews'

    def __str__(self):
        return f"Review for {self.application} by {self.reviewed_by.username}"
