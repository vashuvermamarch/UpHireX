import os
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from uphirex.utils import api_response
from .models import FileUpload
from .serializers import FileUploadSerializer


class FileUploadViewSet(viewsets.ModelViewSet):
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ['entity_type', 'entity_id']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return FileUpload.objects.all()
        return FileUpload.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return api_response(False, "No file provided.", status_code=status.HTTP_400_BAD_REQUEST)

        # Save file to media directory
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', str(request.user.id))
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file_obj.name)

        with open(file_path, 'wb+') as dest:
            for chunk in file_obj.chunks():
                dest.write(chunk)

        relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)

        upload = FileUpload.objects.create(
            user=request.user,
            file_name=file_obj.name,
            file_path=relative_path,
            file_size=file_obj.size,
            mime_type=file_obj.content_type or '',
            entity_id=request.data.get('entity_id', ''),
            entity_type=request.data.get('entity_type', ''),
        )

        return api_response(True, "File uploaded.", FileUploadSerializer(upload).data, status.HTTP_201_CREATED)
