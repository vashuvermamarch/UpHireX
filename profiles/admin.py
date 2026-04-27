from django.contrib import admin
from .models import Profile, Skill, UserSkill, ProfileView


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'location', 'current_company', 'availability_status')
    search_fields = ('user__username', 'headline', 'location')
    list_filter = ('availability_status',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    search_fields = ('name', 'category')
    list_filter = ('category',)
    ordering = ('name',)


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'proficiency_level', 'created_at')
    list_filter = ('proficiency_level',)
    search_fields = ('user__username', 'skill__name')


@admin.register(ProfileView)
class ProfileViewAdmin(admin.ModelAdmin):
    list_display = ('viewer', 'viewed_user', 'viewed_at')
    search_fields = ('viewer__username', 'viewed_user__username')
