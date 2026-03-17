from rest_framework import serializers
from .models import Profile, Skill, UserSkill, ProfileView


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('user', 'updated_at')


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class UserSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = UserSkill
        fields = ('id', 'user', 'skill', 'skill_name', 'proficiency_level', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')


class ProfileViewSerializer(serializers.ModelSerializer):
    viewer_name = serializers.CharField(source='viewer.displayName', read_only=True)

    class Meta:
        model = ProfileView
        fields = ('id', 'viewer', 'viewer_name', 'viewed_user', 'viewed_at')
        read_only_fields = ('id', 'viewer', 'viewed_at')
