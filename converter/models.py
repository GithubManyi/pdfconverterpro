# converter/models.py
"""Models for converter app."""
import os
import uuid
import json
from django.db import models

def upload_to(instance, filename):
    """Generate upload path for files."""
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4().hex[:10]}{ext}"
    return os.path.join('uploads/', filename)

class UploadedFile(models.Model):
    """Store uploaded files."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=upload_to)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True)
    
    def __str__(self):
        return self.original_filename
    
    def delete(self, *args, **kwargs):
        """Delete file from storage when model is deleted."""
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

class ConversionTask(models.Model):
    """Track conversion tasks."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    input_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    output_file = models.FileField(upload_to='converted/', null=True, blank=True)
    conversion_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Add this field for storing conversion options
    extra_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.conversion_type} - {self.status}"
    
    def get_extra_data(self):
        """Get extra data as dictionary."""
        return self.extra_data or {}
    
    def set_extra_data(self, data):
        """Set extra data."""
        self.extra_data = data