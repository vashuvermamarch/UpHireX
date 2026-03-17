from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from uphirex.utils import api_response
from authapp.decorators import IsHROrAdmin, IsAdmin
from .models import Team
from .serializers import TeamSerializer


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsHROrAdmin()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return api_response(False, "Only admin can delete organizations.", status_code=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
