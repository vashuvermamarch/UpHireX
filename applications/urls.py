from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobApplicationViewSet, ApplicationReviewViewSet

router = DefaultRouter()
router.register(r'applications', JobApplicationViewSet, basename='applications')
router.register(r'application-reviews', ApplicationReviewViewSet, basename='application-reviews')

urlpatterns = [path('', include(router.urls))]
