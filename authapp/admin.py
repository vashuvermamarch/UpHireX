from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.conf import settings
from .models import User, RefreshToken, SessionAudit, Admin as AdminModel


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'displayName', 'role', 'is_active', 'email_verified', 'created_at')
    list_filter = ('role', 'is_active', 'email_verified', 'two_factor_enabled')
    search_fields = ('username', 'email', 'displayName', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Uphirex Fields', {'fields': (
            'displayName', 'profile_photo_url', 'bio', 'role',
            'email_verified', 'email_verification_token', 'phone',
            'phone_verified', 'two_factor_secret', 'two_factor_enabled',
            'failed_login_attempts', 'account_locked_until', 'organization_id',
        )}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Uphirex Fields', {'fields': ('email', 'displayName', 'role', 'phone')}),
    )

    def save_model(self, request, obj, form, change):
        if change:
            try:
                old_obj = User.objects.get(pk=obj.pk)
                if old_obj.role == User.Role.HR and not old_obj.is_active and obj.is_active:
                    self._send_activation_email(obj)
            except User.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)

    def _send_activation_email(self, user):
        try:
            send_mail(
                'Account Activated - Uphirex',
                f'Hello {user.displayName or user.username},\n\n'
                f'Your HR account has been activated. You can now login.\n\nThank you!',
                settings.EMAIL_HOST_USER, [user.email],
            )
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.error(f"Failed to send activation email: {e}")


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_revoked', 'ip_address')
    list_filter = ('is_revoked',)
    search_fields = ('user__username', 'user__email')


@admin.register(SessionAudit)
class SessionAuditAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_at', 'logout_at', 'ip_address', 'success')
    list_filter = ('success',)
    search_fields = ('user__username', 'user__email')


@admin.register(AdminModel)
class AdminRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'activated_by', 'activated_at')
    search_fields = ('user__username',)


admin.site.register(User, CustomUserAdmin)
