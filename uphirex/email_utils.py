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


def send_application_status_email(email, display_name, job_title, new_status):
    """
    Sends a premium HTML application status update email to the user.
    """
    subject = f"Update on your Application: {job_title} | UpHireZ"
    
    status_configs = {
        'reviewed': {
            'title': "Application Reviewed",
            'message': "Your application has been successfully reviewed by our HR team. We are currently evaluating all candidates.",
            'color': "#3b82f6" # Blue
        },
        'shortlisted': {
            'title': "You've Been Shortlisted!",
            'message': "Great news! Your profile stood out, and we've shortlisted you for the next round. Our team will reach out shortly with the next steps.",
            'color': "#8b5cf6" # Purple
        },
        'accepted': {
            'title': "Congratulations! You're Hired!",
            'message': "We are thrilled to inform you that your application has been accepted. We believe you'll be a fantastic addition to our team!",
            'color': "#10b981" # Green
        },
        'rejected': {
            'title': "Application Update",
            'message': "Thank you for your interest in the position. After careful consideration, we've decided to move forward with other candidates at this time. We wish you the best in your search.",
            'color': "#ef4444" # Red
        },
        'pending': {
            'title': "Application Received",
            'message': "Your application is currently being processed by our system. You will receive an update as soon as the review is complete.",
            'color': "#6b7280" # Gray
        }
    }
    
    config = status_configs.get(new_status, {
        'title': f"Status Updated: {new_status.capitalize()}",
        'message': f"Your application status for '{job_title}' has been updated to {new_status}.",
        'color': "#3b82f6"
    })
    
    html_message = f"""
    <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px; background-color: #0f172a; color: #f8fafc; border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #ffffff; font-size: 28px; font-weight: 800; margin: 0; letter-spacing: -1px;">UpHire<span style="color: #3b82f6;">Z</span></h1>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 5px;">Elevating Your Career Path</p>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 16px; border-left: 4px solid {config['color']};">
            <h2 style="color: {config['color']}; margin-top: 0; font-size: 22px;">{config['title']}</h2>
            <p style="font-size: 16px; line-height: 1.6;">Hello <strong>{display_name}</strong>,</p>
            <p style="font-size: 16px; line-height: 1.6; color: #e2e8f0;">{config['message']}</p>
            
            <div style="margin-top: 25px; padding: 20px; background: rgba(255, 255, 255, 0.03); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05);">
                <p style="margin: 0; font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Position Applied For</p>
                <p style="margin: 8px 0 0 0; font-size: 18px; font-weight: 600; color: #ffffff;">{job_title}</p>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 35px;">
            <a href="http://localhost:3000/dashboard" style="display: inline-block; padding: 14px 35px; background-color: #3b82f6; color: #ffffff; text-decoration: none; border-radius: 12px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.39);">View Application Status</a>
        </div>
        
        <div style="margin-top: 40px; text-align: center; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 20px;">
            <p style="color: #64748b; font-size: 12px; line-height: 1.5;">
                &copy; 2026 UpHireZ Platform. All rights reserved.<br>
                This is an automated notification from the UpHireZ system.<br>
                Please do not reply directly to this email.
            </p>
        </div>
    </div>
    """
    
    # Plain text fallback
    plain_message = f"""
    Hello {display_name},
    
    {config['title']}
    
    {config['message']}
    
    Position: {job_title}
    
    Visit your dashboard for more details: http://localhost:3000/dashboard
    
    Best regards,
    The UpHireZ Team
    """
    
    from_email = settings.EMAIL_HOST_USER
    
    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            [email],
            fail_silently=False,
            html_message=html_message
        )
        logger.info(f"Premium status update email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send premium status update email to {email}: {str(e)}")
        return False
