#!/usr/bin/env python
"""
Auto-cleanup script for old files.
Run as cron job: python scripts/cleanup.py
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add project to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from converter.models import UploadedFile, ConversionTask

def cleanup_files():
    """Delete files older than 1 hour."""
    one_hour_ago = datetime.now() - timedelta(hours=1)
    
    # Delete old uploaded files
    old_files = UploadedFile.objects.filter(uploaded_at__lt=one_hour_ago)
    file_count = old_files.count()
    for file in old_files:
        file.delete()
    
    # Delete old conversion tasks
    old_tasks = ConversionTask.objects.filter(created_at__lt=one_hour_ago)
    task_count = old_tasks.count()
    old_tasks.delete()
    
    print(f"[{datetime.now()}] Cleanup completed:")
    print(f"  - Deleted {file_count} uploaded files")
    print(f"  - Deleted {task_count} conversion tasks")
    
    # Clean empty directories
    media_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media')
    for root, dirs, files in os.walk(media_root, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)

if __name__ == '__main__':
    cleanup_files()