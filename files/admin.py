from django.contrib import admin
from .models import FileUpload


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'user', 'file_size', 'mime_type', 'entity_type', 'uploaded_at')
    list_filter = ('entity_type', 'mime_type')
    search_fields = ('file_name', 'user__username')
