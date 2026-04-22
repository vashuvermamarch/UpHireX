from django.urls import path
from .views import AIAssistantView

urlpatterns = [
    path('ai/assistant/', AIAssistantView.as_view(), name='ai-assistant'),
]
