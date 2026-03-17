from rest_framework import serializers
from .models import JobApplication, ApplicationReview


class JobApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='user.displayName', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ('id', 'user', 'applied_at', 'updated_at')


class ApplicationReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewed_by.displayName', read_only=True)

    class Meta:
        model = ApplicationReview
        fields = '__all__'
        read_only_fields = ('id', 'reviewed_by', 'reviewed_at')
