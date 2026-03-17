from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from uphirex.utils import api_response
from authapp.decorators import IsHR, IsHROrAdmin, IsAdmin
from .models import JobPost, JobSkill, SavedJob
from .serializers import JobPostSerializer, JobSkillSerializer, SavedJobSerializer
from .services.adzuna_service import search_adzuna_jobs


class JobPostViewSet(viewsets.ModelViewSet):
    serializer_class = JobPostSerializer
    filterset_fields = ['status', 'remote', 'location']
    search_fields = ['title', 'description', 'requirements']
    ordering_fields = ['created_at', 'title']

    def get_queryset(self):
        return JobPost.objects.select_related('posted_by', 'organization_id').all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), IsHROrAdmin()]

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user, organization_id=self.request.user.organization_id)

    def update(self, request, *args, **kwargs):
        job = self.get_object()
        if job.posted_by != request.user and request.user.role != 'admin':
            return api_response(False, "Only the owner or admin can edit.", status_code=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """Merge internal jobs with Adzuna external jobs."""
        # Internal jobs
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            internal = JobPostSerializer(page, many=True).data
        else:
            internal = JobPostSerializer(queryset, many=True).data

        # Mark internal jobs
        for job in internal:
            job['source'] = 'internal'

        # External jobs from Adzuna
        query = request.query_params.get('search', '')
        location = request.query_params.get('location', '')
        external = search_adzuna_jobs(query=query, location=location)

        merged = internal + external
        return api_response(True, "Jobs retrieved.", merged, status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def save_job(self, request, pk=None):
        job = self.get_object()
        saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
        if not created:
            return api_response(False, "Job already saved.", status_code=status.HTTP_400_BAD_REQUEST)
        return api_response(True, "Job saved.", SavedJobSerializer(saved).data, status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def unsave_job(self, request, pk=None):
        job = self.get_object()
        deleted, _ = SavedJob.objects.filter(user=request.user, job=job).delete()
        if deleted:
            return api_response(True, "Job unsaved.", status_code=status.HTTP_200_OK)
        return api_response(False, "Job was not saved.", status_code=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def saved(self, request):
        saved = SavedJob.objects.filter(user=request.user).select_related('job')
        return api_response(True, "Saved jobs.", SavedJobSerializer(saved, many=True).data, status.HTTP_200_OK)


class JobSkillViewSet(viewsets.ModelViewSet):
    serializer_class = JobSkillSerializer
    permission_classes = [IsAuthenticated, IsHROrAdmin]
    queryset = JobSkill.objects.select_related('job', 'skill').all()
    filterset_fields = ['job', 'is_required']
