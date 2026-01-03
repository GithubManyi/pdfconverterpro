"""
Security utilities for PDF Converter Pro
"""
import os
import magic
import hashlib
import mimetypes
from django.core.exceptions import ValidationError, SuspiciousOperation
from django.core.files.uploadedfile import UploadedFile
from pathlib import Path
import tempfile
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class SecureFileValidator:
    """
    Comprehensive file validation for security
    """
    
    # Allowed MIME types with their corresponding extensions
    ALLOWED_MIME_TYPES = {
        'application/pdf': ['.pdf'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        'application/msword': ['.doc'],
        'application/vnd.ms-excel': ['.xls'],
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
        'image/tiff': ['.tiff', '.tif'],
        'image/bmp': ['.bmp'],
        'image/webp': ['.webp'],
        'application/zip': ['.xlsx', '.docx'],  # Office files are ZIP archives
        'application/x-zip-compressed': ['.xlsx', '.docx'],  # Alternative MIME type
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'image': 10 * 1024 * 1024,  # 10MB for images
        'pdf': 50 * 1024 * 1024,    # 50MB for PDFs
        'document': 20 * 1024 * 1024, # 20MB for office docs
    }
    
    # Blocked dangerous extensions
    DANGEROUS_EXTENSIONS = [
        '.exe', '.bat', '.cmd', '.sh', '.php', '.py', '.js', '.html',
        '.htm', '.jar', '.war', '.ear', '.dll', '.so', '.bin', '.app'
    ]
    
    @classmethod
    def validate_file(cls, file: UploadedFile) -> Dict:
        """
        Validate file for security
        
        Returns: {
            'is_valid': bool,
            'mime_type': str,
            'real_extension': str,
            'errors': list
        }
        """
        errors = []
        
        # 1. Check file extension
        original_name = file.name.lower()
        original_ext = Path(original_name).suffix
        
        # Block dangerous extensions
        if any(original_ext.endswith(ext) for ext in cls.DANGEROUS_EXTENSIONS):
            errors.append(f"Dangerous file extension: {original_ext}")
            return {'is_valid': False, 'errors': errors}
        
        # 2. Check file size based on type
        file_size = file.size
        
        # Read first 2048 bytes for MIME detection
        file_content = file.read(2048)
        file.seek(0)  # Reset file pointer
        
        # 3. Detect real MIME type using magic
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
        except Exception as e:
            logger.error(f"Error detecting MIME type: {e}")
            # Fallback to Python's mimetypes
            mime_type, _ = mimetypes.guess_type(original_name)
            if not mime_type:
                errors.append("Unable to determine file type")
                return {'is_valid': False, 'errors': errors}
        
        # 4. Check if MIME type is allowed
        if mime_type not in cls.ALLOWED_MIME_TYPES:
            errors.append(f"Unsupported file type: {mime_type}")
            return {'is_valid': False, 'errors': errors}
        
        # 5. Get allowed extensions for this MIME type
        allowed_extensions = cls.ALLOWED_MIME_TYPES.get(mime_type, [])
        
        # 6. Check if extension matches MIME type
        if original_ext not in allowed_extensions:
            # Try to get correct extension from MIME type
            correct_ext = allowed_extensions[0] if allowed_extensions else '.unknown'
            errors.append(f"File extension {original_ext} doesn't match file type {mime_type}. Expected: {correct_ext}")
            return {'is_valid': False, 'errors': errors}
        
        # 7. Check file size based on file type category
        if 'image' in mime_type:
            max_size = cls.MAX_FILE_SIZES['image']
            category = 'image'
        elif 'pdf' in mime_type:
            max_size = cls.MAX_FILE_SIZES['pdf']
            category = 'pdf'
        else:
            max_size = cls.MAX_FILE_SIZES['document']
            category = 'document'
        
        if file_size > max_size:
            mb_size = max_size / 1024 / 1024
            errors.append(f"File too large for {category} type. Maximum size is {mb_size}MB")
            return {'is_valid': False, 'errors': errors}
        
        # 8. Calculate file hash for tracking
        file.seek(0)
        file_hash = hashlib.sha256(file.read()).hexdigest()
        file.seek(0)
        
        return {
            'is_valid': True,
            'mime_type': mime_type,
            'real_extension': original_ext,
            'category': category,
            'file_hash': file_hash,
            'errors': errors
        }


class FilePathSecurity:
    """
    Prevent directory traversal attacks
    """
    
    @staticmethod
    def sanitize_path(user_input: str) -> str:
        """
        Sanitize file paths to prevent directory traversal
        """
        # Normalize path
        path = Path(user_input).resolve()
        
        # Check for directory traversal attempts
        if '..' in str(path) or path.is_absolute():
            raise SuspiciousOperation("Invalid file path")
        
        return str(path)
    
    @staticmethod
    def is_safe_within_directory(base_path: str, target_path: str) -> bool:
        """
        Check if target_path is within base_path
        """
        try:
            base = Path(base_path).resolve()
            target = Path(target_path).resolve()
            
            # Check if target is within base
            return base in target.parents or base == target
        except Exception:
            return False


class AntiAbuseSystem:
    """
    Prevent abuse and rate limiting
    """
    
    def __init__(self, ip_address: str):
        self.ip_address = ip_address
        self.redis_client = None  # You can connect to Redis here
    
    def check_rate_limit(self, operation: str, limit: int = 10, window: int = 60) -> bool:
        """
        Check if IP has exceeded rate limit
        """
        # Implement with Redis or Django cache
        from django.core.cache import cache
        
        cache_key = f"rate_limit:{self.ip_address}:{operation}"
        requests = cache.get(cache_key, 0)
        
        if requests >= limit:
            logger.warning(f"Rate limit exceeded for IP {self.ip_address}, operation: {operation}")
            return False
        
        cache.set(cache_key, requests + 1, window)
        return True
    
    def track_conversion(self, file_hash: str) -> bool:
        """
        Track conversions to prevent duplicate abuse
        """
        # You can implement this to prevent mass conversion of same file
        pass


def create_secure_temp_file() -> Tuple[str, str]:
    """
    Create a secure temporary file with proper permissions
    """
    # Create temp directory with secure permissions
    temp_dir = tempfile.mkdtemp(prefix='pdfconverter_')
    
    # Set directory permissions
    os.chmod(temp_dir, 0o700)
    
    # Create temp file
    fd, temp_path = tempfile.mkstemp(dir=temp_dir, suffix='.tmp')
    os.close(fd)
    
    return temp_dir, temp_path


def cleanup_secure_temp(temp_dir: str):
    """
    Clean up temporary directory securely
    """
    try:
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        logger.error(f"Error cleaning up temp directory {temp_dir}: {e}")