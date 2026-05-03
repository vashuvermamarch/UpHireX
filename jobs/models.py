import uuid
from django.db import models
from django.conf import settings


class JobPost(models.Model):
    """Job posting per schema."""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'
        DRAFT = 'draft', 'Draft'

    class HiringType(models.TextChoices):
        JOB = 'job', 'Job'
        INTERNSHIP = 'internship', 'Internship'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    requirements = models.TextField(blank=True, default='')
    salary_range = models.CharField(max_length=100, blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    remote = models.BooleanField(default=False)
    external_url = models.URLField(max_length=500, blank=True, default='')
    hiring_type = models.CharField(
        max_length=20,
        choices=HiringType.choices,
        default=HiringType.JOB
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='job_posts',
    )
    organization_id = models.ForeignKey(
        'organizations.Team', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='job_posts',
        db_column='organization_id',
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'job_posts'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['posted_by']),
            models.Index(fields=['organization_id']),
        ]

    def __str__(self):
        return self.title


class JobSkill(models.Model):
    """Job-skill linkage per schema."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='job_skills')
    skill = models.ForeignKey('profiles.Skill', on_delete=models.CASCADE, related_name='job_skills')
    is_required = models.BooleanField(default=True)

    class Meta:
        db_table = 'job_skills'
        unique_together = ('job', 'skill')

    def __str__(self):
        return f"{self.job.title} - {self.skill.name}"


class SavedJob(models.Model):
    """Saved/bookmarked job per schema."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='saved_jobs',
    )
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_jobs'
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
