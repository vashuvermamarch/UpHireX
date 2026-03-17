from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from uphirex.utils import api_response
from .services.youtube_service import search_youtube_courses


class CourseSearchView(APIView):
    """Search YouTube playlists as courses. GET /api/v1/courses/?query=python"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('query', '')
        if not query:
            return api_response(False, "Query parameter required.", status_code=status.HTTP_400_BAD_REQUEST)

        max_results = int(request.query_params.get('max_results', 20))
        courses = search_youtube_courses(query, max_results=max_results)
        return api_response(True, "Courses retrieved.", courses, status.HTTP_200_OK)
