from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_otp_email(email, otp):
    """
    Sends a one-time password (OTP) to the user's email.
    """
    subject = "Verify your UpHireZ account"
    message = f"""
    Hello,

    Thank you for signing up for UpHireZ!

    Your verification code is: {otp}

    This code will expire in 5 minutes.

    If you did not request this code, please ignore this email.

    Best regards,
    The UpHireZ Team
    """
    from_email = settings.EMAIL_HOST_USER
    
    try:
        send_mail(
            subject,
            message,
            from_email,
            [email],
            fail_silently=False,
        )
        logger.info(f"OTP email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        return False


def send_activation_email(email, display_name):
    """
    Sends an account activation notification to the user.
    """
    subject = "Your UpHireZ HR Account is Active!"
    message = f"""
    Hello {display_name},

    Great news! Your HR account on UpHireZ has been activated by our administrators.

    You can now log in to your dashboard and start posting jobs and managing candidates.

    Login here: http://localhost:8000/auth/login/ (or your frontend URL)

    Welcome aboard!

    Best regards,
    The UpHireZ Team
    """
    from_email = settings.EMAIL_HOST_USER
    
    try:
        send_mail(
            subject,
            message,
            from_email,
            [email],
            fail_silently=False,
        )
        logger.info(f"Activation email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send activation email to {email}: {str(e)}")
        return False
