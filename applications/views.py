from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from uphirex.utils import api_response
from authapp.decorators import IsHROrAdmin, IsJobSeeker
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
        if JobApplication.objects.filter(user=request.user, job_id=job_id).exists():
            return api_response(False, "Already applied to this job.", status_code=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
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
        application.status = new_status
        application.save(update_fields=['status', 'updated_at'])
        return api_response(True, "Status updated.", JobApplicationSerializer(application).data, status.HTTP_200_OK)


class ApplicationReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationReviewSerializer
    permission_classes = [IsAuthenticated, IsHROrAdmin]
    queryset = ApplicationReview.objects.select_related('application', 'reviewed_by').all()
    filterset_fields = ['application']

    def perform_create(self, serializer):
        serializer.save(reviewed_by=self.request.user)
