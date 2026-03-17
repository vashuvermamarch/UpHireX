from django.contrib import admin
from .models import JobApplication, ApplicationReview


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'status', 'applied_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'job__title')


@admin.register(ApplicationReview)
class ApplicationReviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'reviewed_by', 'reviewed_at')
    search_fields = ('reviewed_by__username',)
