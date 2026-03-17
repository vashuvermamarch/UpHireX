from django.contrib import admin
from .models import JobPost, JobSkill, SavedJob


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'organization_id', 'status', 'remote', 'created_at')
    list_filter = ('status', 'remote')
    search_fields = ('title', 'description', 'location')


@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):
    list_display = ('job', 'skill', 'is_required')
    list_filter = ('is_required',)
    search_fields = ('job__title', 'skill__name')


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'saved_at')
    search_fields = ('user__username', 'job__title')
