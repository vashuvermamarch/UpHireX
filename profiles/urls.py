from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, SkillViewSet, UserSkillViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profiles')
router.register(r'skills', SkillViewSet, basename='skills')
router.register(r'user-skills', UserSkillViewSet, basename='user-skills')

urlpatterns = [path('', include(router.urls))]
