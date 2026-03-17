from django.urls import path
from .views import CourseSearchView

urlpatterns = [
    path('courses/', CourseSearchView.as_view(), name='course-search'),
]
