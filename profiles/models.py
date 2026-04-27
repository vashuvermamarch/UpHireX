import uuid
from django.db import models
from django.conf import settings


class Profile(models.Model):
    """User profile per schema. PK is user_id."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        primary_key=True, related_name='profile',
    )
    headline = models.CharField(max_length=255, blank=True, default='')
    summary = models.TextField(blank=True, default='')
    resume_url = models.URLField(max_length=500, blank=True, default='')
    linked_profiles = models.JSONField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, default='')
    current_company = models.CharField(max_length=255, blank=True, default='')
    total_experience = models.IntegerField(default=0)
    availability_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('busy', 'Busy'),
            ('unavailable', 'Unavailable'),
            ('open_to_work', 'Open to Work'),
            ('hired', 'Hired')
        ],
        default='active',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return f"Profile: {self.user.username}"


class Skill(models.Model):
    """Global skill per schema."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'skills'
        verbose_name = "Platform Skill"
        verbose_name_plural = "Platform Skills"
        ordering = ['name']

    def __str__(self):
        return self.name


class UserSkill(models.Model):
    """User-skill linkage per schema."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='user_skills',
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='user_skills')
    proficiency_level = models.CharField(
        max_length=20,
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('expert', 'Expert')],
        default='beginner',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_skills'
        unique_together = ('user', 'skill')

    def __str__(self):
        return f"{self.user.username} - {self.skill.name}"


class ProfileView(models.Model):
    """Profile view tracking per schema."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='profile_views_made',
    )
    viewed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='profile_views_received',
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'profile_views'

    def __str__(self):
        return f"{self.viewer.username} viewed {self.viewed_user.username}"
