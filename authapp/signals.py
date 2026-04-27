from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User
from uphirex.email_utils import send_activation_email

@receiver(pre_save, sender=User)
def handle_user_activation(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            # Check if is_active changed from False to True
            if not old_instance.is_active and instance.is_active:
                # Only send for HR role (as requested)
                if instance.role == User.Role.HR:
                    send_activation_email(instance.email, instance.displayName or instance.username)
        except User.DoesNotExist:
            pass
