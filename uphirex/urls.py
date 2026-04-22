"""
Uphirex URL Configuration.
All API routes under /api/v1/.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        "success": True,
        "message": "Welcome to Uphirex API v1",
        "endpoints": [
            "/api/v1/auth/signup/",
            "/api/v1/auth/login/",
            "/api/v1/jobs/",
            "/api/v1/profiles/",
            "/api/v1/organizations/",
            "/api/v1/ai/assistant/"
        ]
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),

    # ── API v1 ────────────────────────────────────────
    path('api/v1/', include('authapp.urls')),
    path('api/v1/', include('organizations.urls')),
    path('api/v1/', include('profiles.urls')),
    path('api/v1/', include('connections.urls')),
    path('api/v1/', include('jobs.urls')),
    path('api/v1/', include('applications.urls')),
    path('api/v1/', include('chat.urls')),
    path('api/v1/', include('notifications.urls')),
    path('api/v1/', include('files.urls')),
    path('api/v1/', include('courses.urls')),
    path('api/v1/', include('ai.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
