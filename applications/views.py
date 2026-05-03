from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from uphirex.utils import api_response
from authapp.decorators import IsHROrAdmin, IsJobSeeker
from notifications.utils import create_notification
from .models import JobApplication, ApplicationReview
from .serializers import JobApplicationSerializer, ApplicationReviewSerializer


class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    filterset_fields = ['status', 'job']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'job_seeker':
            return JobApplication.objects.filter(user=user).select_related('job', 'user')
        return JobApplication.objects.select_related('job', 'user').all()

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsJobSeeker()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        job_id = request.data.get('job')
        from jobs.utils import get_or_create_shadow_job
        job, error = get_or_create_shadow_job(job_id, requester=request.user)
        
        if error:
            return api_response(False, error, status_code=status.HTTP_404_NOT_FOUND)

        if JobApplication.objects.filter(user=request.user, job=job).exists():
            return api_response(False, "Already applied to this job.", status_code=status.HTTP_400_BAD_REQUEST)
        
        # Inject the internal job UUID into data for serializer validation
        data = request.data.copy()
        data['job'] = job.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save(user=request.user)

        # Notification for HR (Job Poster)
        if job.posted_by:
            create_notification(
                user=job.posted_by,
                n_type='job_applied',
                from_user=request.user,
                message=f"{request.user.displayName or request.user.username} applied for your job: {job.title}",
                reference_id=application.id,
                reference_type='application'
            )

        return api_response(True, "Application submitted.", serializer.data, status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """HR/Admin updates application status."""
        if request.user.role not in ('hr', 'admin'):
            return api_response(False, "Only HR/Admin can update status.", status_code=status.HTTP_403_FORBIDDEN)
        application = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(JobApplication.Status.choices):
            return api_response(False, "Invalid status.", status_code=status.HTTP_400_BAD_REQUEST)
        
        old_status = application.status
        application.status = new_status
        application.save(update_fields=['status', 'updated_at'])

        # Notification for Job Seeker (Applicant)
        if old_status != new_status:
            create_notification(
                user=application.user,
                n_type='application_status',
                from_user=request.user,
                message=f"Your application for {application.job.title} status updated to: {new_status}",
                reference_id=application.id,
                reference_type='application'
            )
            
            # Send Email
            from uphirex.email_utils import send_application_status_email
            send_application_status_email(
                email=application.user.email,
                display_name=application.user.displayName or application.user.username,
                job_title=application.job.title,
                new_status=new_status
            )

        return api_response(True, "Status updated.", JobApplicationSerializer(application).data, status.HTTP_200_OK)


class ApplicationReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationReviewSerializer
    permission_classes = [IsAuthenticated, IsHROrAdmin]
    queryset = ApplicationReview.objects.select_related('application', 'reviewed_by').all()
    filterset_fields = ['application']

    def perform_create(self, serializer):
        serializer.save(reviewed_by=self.request.user)
