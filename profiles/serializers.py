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
    skill_name = serializers.CharField(required=False)

    class Meta:
        model = UserSkill
        fields = ('id', 'user', 'skill', 'skill_name', 'proficiency_level', 'created_at')
        read_only_fields = ('id', 'user', 'created_at', 'skill')

    def validate(self, data):
        skill_name = data.get('skill_name')
        skill_id = data.get('skill')

        if not skill_id and not skill_name:
            raise serializers.ValidationError("Either skill (ID) or skill_name must be provided.")

        if skill_name:
            try:
                skill = Skill.objects.get(name__iexact=skill_name)
                data['skill'] = skill
            except Skill.DoesNotExist:
                raise serializers.ValidationError(f"Skill '{skill_name}' does not exist. Please contact an admin to add it.")
        
        # Remove skill_name from data as it's not a model field
        data.pop('skill_name', None)
        return data

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['skill_name'] = instance.skill.name
        return repr


class ProfileViewSerializer(serializers.ModelSerializer):
    viewer_name = serializers.CharField(source='viewer.displayName', read_only=True)

    class Meta:
        model = ProfileView
        fields = ('id', 'viewer', 'viewer_name', 'viewed_user', 'viewed_at')
        read_only_fields = ('id', 'viewer', 'viewed_at')
