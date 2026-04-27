from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from uphirex.utils import api_response
from authapp.decorators import IsOwnerOrAdmin, IsAdmin
from notifications.utils import create_notification
from .models import Profile, Skill, UserSkill, ProfileView
from .serializers import ProfileSerializer, SkillSerializer, UserSkillSerializer, ProfileViewSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.select_related('user').all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Track profile view
        if instance.user != request.user:
            ProfileView.objects.create(viewer=request.user, viewed_user=instance.user)
            # Create Notification
            create_notification(
                user=instance.user,
                n_type='profile_view',
                from_user=request.user,
                message=f"{request.user.displayName or request.user.username} viewed your profile.",
                reference_id=instance.user.id,
                reference_type='profile'
            )
        serializer = self.get_serializer(instance)
        return api_response(True, "Profile retrieved.", serializer.data, status.HTTP_200_OK)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        if request.method == 'PATCH':
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return api_response(True, "Profile updated.", serializer.data, status.HTTP_200_OK)
        return api_response(True, "Your profile.", ProfileSerializer(profile).data, status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def views(self, request, pk=None):
        """Get who viewed this profile."""
        profile = self.get_object()
        if profile.user != request.user and request.user.role != 'admin':
            return api_response(False, "Access denied.", status_code=status.HTTP_403_FORBIDDEN)
        views = ProfileView.objects.filter(viewed_user=profile.user).select_related('viewer')[:50]
        return api_response(True, "Profile views.", ProfileViewSerializer(views, many=True).data, status.HTTP_200_OK)


class SkillViewSet(viewsets.ModelViewSet):
    serializer_class = SkillSerializer
    queryset = Skill.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category']
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return api_response(True, "Skills retrieved.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(True, "Skill created.", serializer.data, status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(True, "Skill details.", serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return api_response(True, "Skill updated.", serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return api_response(True, "Skill deleted.", status_code=status.HTTP_204_NO_CONTENT)


class UserSkillViewSet(viewsets.ModelViewSet):
    serializer_class = UserSkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user).select_related('skill')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(True, "Your skills retrieved.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(True, "Skill added to your profile.", serializer.data, status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(True, "User skill details.", serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return api_response(True, "User skill updated.", serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return api_response(True, "Skill removed from your profile.", status_code=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path=r'user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        skills = UserSkill.objects.filter(user_id=user_id).select_related('skill')
        return api_response(True, "User skills.", UserSkillSerializer(skills, many=True).data, status.HTTP_200_OK)
