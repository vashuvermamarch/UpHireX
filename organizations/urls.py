from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet

router = DefaultRouter()
router.register(r'organizations', TeamViewSet, basename='organizations')

urlpatterns = [path('', include(router.urls))]
