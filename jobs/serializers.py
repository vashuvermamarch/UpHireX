from rest_framework import serializers
from .models import JobPost, JobSkill, SavedJob


class JobPostSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(source='posted_by.displayName', read_only=True)
    organization_name = serializers.CharField(source='organization_id.name', read_only=True, default='')

    class Meta:
        model = JobPost
        fields = '__all__'
        read_only_fields = ('id', 'posted_by', 'created_at', 'updated_at')


class JobSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = JobSkill
        fields = ('id', 'job', 'skill', 'skill_name', 'is_required')
        read_only_fields = ('id',)


class SavedJobSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = SavedJob
        fields = ('id', 'user', 'job', 'job_title', 'saved_at')
        read_only_fields = ('id', 'user', 'saved_at')


class ExternalJobSerializer(serializers.Serializer):
    """For Adzuna external jobs (not stored in DB)."""
    title = serializers.CharField()
    company = serializers.CharField()
    location = serializers.CharField()
    salary = serializers.CharField()
    apply_url = serializers.URLField()
    description = serializers.CharField()
    source = serializers.CharField()
    created_at = serializers.CharField()
