from django.contrib import admin
from .models import Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'location', 'is_verified', 'created_by', 'created_at')
    list_filter = ('is_verified', 'industry')
    search_fields = ('name', 'industry', 'location')
