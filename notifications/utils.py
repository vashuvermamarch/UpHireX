from .models import Notification

def create_notification(user, n_type, from_user=None, message='', reference_id='', reference_type=''):
    """
    Utility to create a notification record.
    """
    return Notification.objects.create(
        user=user,
        type=n_type,
        from_user=from_user,
        message=message,
        reference_id=str(reference_id),
        reference_type=reference_type
    )
