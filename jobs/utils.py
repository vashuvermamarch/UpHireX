import logging
from django.conf import settings
from authapp.models import User
from .models import JobPost
from .services.adzuna_service import search_adzuna_jobs

logger = logging.getLogger(__name__)

def get_or_create_shadow_job(job_id, requester=None):
    """
    Checks if job_id is internal or external (adzuna:).
    If external, ensures a local JobPost record exists.
    Returns (job_instance, error_message)
    """
    if not str(job_id).startswith('adzuna:'):
        try:
            return JobPost.objects.get(id=job_id), None
        except (JobPost.DoesNotExist, ValueError):
            return None, f"Job with ID {job_id} does not exist."

    # External Adzuna job
    job = JobPost.objects.filter(external_id=job_id).first()
    if job:
        return job, None

    # Fetch from Adzuna service
    job_data = next((j for j in search_adzuna_jobs() if j['id'] == job_id), None)
    if not job_data:
        return None, "Adzuna job not found or expired."

    # Create shadow record
    # Find an admin to own the post
    admin_user = User.objects.filter(role='admin').first()
    if not admin_user and requester and requester.is_authenticated:
        admin_user = requester

    if not admin_user:
        return None, "System error: No admin user found to shadow external job."

    job = JobPost.objects.create(
        external_id=job_id,
        title=job_data['title'],
        description=job_data['description'],
        location=job_data['location'],
        salary_range=job_data['salary_range'],
        posted_by=admin_user,
        status='active'
    )
    return job, None
