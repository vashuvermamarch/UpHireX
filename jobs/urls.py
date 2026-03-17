from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobPostViewSet, JobSkillViewSet

router = DefaultRouter()
router.register(r'jobs', JobPostViewSet, basename='jobs')
router.register(r'job-skills', JobSkillViewSet, basename='job-skills')

urlpatterns = [path('', include(router.urls))]
