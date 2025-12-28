"""Admin configuration for converter app."""
from django.contrib import admin
from .models import UploadedFile, ConversionTask

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'file_type', 'uploaded_at', 'session_key')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('original_filename', 'session_key')

@admin.register(ConversionTask)
class ConversionTaskAdmin(admin.ModelAdmin):
    list_display = ('conversion_type', 'status', 'created_at', 'completed_at')
    list_filter = ('conversion_type', 'status', 'created_at')
    search_fields = ('conversion_type', 'status')