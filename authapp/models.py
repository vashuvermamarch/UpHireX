import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom User model matching the Uphirex schema exactly."""

    class Role(models.TextChoices):
        JOB_SEEKER = 'job_seeker', _('Job Seeker')
        HR = 'hr', _('HR')
        ADMIN = 'admin', _('Admin')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    displayName = models.CharField(max_length=255, blank=True, default='')
    profile_photo_url = models.URLField(max_length=500, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.JOB_SEEKER,
    )
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    phone_verified = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=255, blank=True, default='')
    two_factor_enabled = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    organization_id = models.ForeignKey(
        'organizations.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        db_column='organization_id',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['organization_id']),
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"


class RefreshToken(models.Model):
    """Refresh tokens stored in DB per schema."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token_hash = models.CharField(max_length=512, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    is_revoked = models.BooleanField(default=False)
    device_info = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'refresh_tokens'
        indexes = [
            models.Index(fields=['token_hash']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"RefreshToken for {self.user.username}"


class SessionAudit(models.Model):
    """Session audit trail per schema."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_audits')
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    success = models.BooleanField(default=True)

    class Meta:
        db_table = 'session_audits'
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Session for {self.user.username} at {self.login_at}"


class Admin(models.Model):
    """Admin activation record per schema."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='admin_record')
    activated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='activated_admins',
    )
    activated_at = models.DateTimeField(auto_now_add=True)
    permissions = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'admins'

    def __str__(self):
        return f"Admin: {self.user.username}"
