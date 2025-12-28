"""
Django settings for pdfconverterpro project.
Production-ready with automatic local/dev/production detection.
"""

import os
import sys
import dj_database_url
from pathlib import Path
from datetime import timedelta

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ============ ENVIRONMENT DETECTION ============
IS_LOCAL = os.getenv('ENVIRONMENT') == 'local' or not os.getenv('ENVIRONMENT')
IS_DEVELOPMENT = os.getenv('ENVIRONMENT') == 'development'
IS_PRODUCTION = os.getenv('ENVIRONMENT') == 'production' or os.getenv('RENDER')

# ============ SECRET KEY ============
# Never hardcode! Load from environment with fallback for local dev
if IS_LOCAL:
    # Try to load from .env file for local development
    try:
        from dotenv import load_dotenv
        load_dotenv(BASE_DIR / '.env')
    except ImportError:
        pass  # dotenv not installed, use environment variables

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if IS_LOCAL:
        # Generate a temporary key for local dev (will be different each time)
        print("WARNING: Using temporary SECRET_KEY for local development")
        print("Create a .env file with SECRET_KEY=your-secret-key-here")
        SECRET_KEY = 'django-insecure-local-dev-key-' + os.urandom(32).hex()[:50]
    else:
        raise ValueError("SECRET_KEY must be set in environment variables")

# ============ DEBUG MODE ============
# Auto-detect debug mode from environment
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
if not DEBUG and (IS_LOCAL or IS_DEVELOPMENT):
    DEBUG = True  # Force debug in local/development

# ============ ALLOWED HOSTS ============
# Production: Only allow specific hosts
# Development: Allow common local hosts
ALLOWED_HOSTS = []

# Render production host
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Your custom domain (set in Render or environment)
CUSTOM_DOMAIN = os.getenv('CUSTOM_DOMAIN')
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

# Local development hosts
if DEBUG or IS_LOCAL:
    ALLOWED_HOSTS.extend([
        'localhost',
        '127.0.0.1',
        '[::1]',
        '0.0.0.0',
        'testserver',
    ])

# ============ CSRF TRUSTED ORIGINS ============
CSRF_TRUSTED_ORIGINS = []

# Render origin
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

# Custom domain origin
if CUSTOM_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f'https://{CUSTOM_DOMAIN}')

# Local development
if DEBUG or IS_LOCAL:
    CSRF_TRUSTED_ORIGINS.extend([
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ])

# Additional origins from environment
CSRF_EXTRA_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if CSRF_EXTRA_ORIGINS:
    CSRF_TRUSTED_ORIGINS.extend(CSRF_EXTRA_ORIGINS.split(','))

# ============ APPLICATION DEFINITION ============
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'django_cleanup.apps.CleanupConfig',
    'widget_tweaks',
    'corsheaders',
    'axes',
    
    # Local apps
    'home.apps.HomeConfig',
    'converter.apps.ConverterConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'home' / 'templates',
            BASE_DIR / 'converter' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.context_processors.site_info',
            ],
            'builtins': [
                'django.templatetags.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ============ DATABASE ============
# Default to SQLite for local development

BASE_DIR = Path(__file__).resolve().parent.parent

# Default SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Override if DATABASE_URL exists (for PostgreSQL on Render)
if os.getenv("DATABASE_URL"):
    db_from_env = dj_database_url.parse(os.getenv("DATABASE_URL"))
    if db_from_env["ENGINE"].startswith("django.db.backends.postgresql"):
        # Only pass sslmode for PostgreSQL
        DATABASES["default"] = dj_database_url.config(conn_max_age=600, conn_health_checks=True)


# ============ PASSWORD VALIDATION ============
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8 if DEBUG else 12,  # Shorter for dev, longer for prod
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Password hashers (Argon2 is best but needs libsodium)
if IS_PRODUCTION:
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.Argon2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    ]
else:
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    ]

# ============ INTERNATIONALIZATION ============
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============ STATIC FILES ============
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Additional static directories
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

# ============ MEDIA FILES ============
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Create media and temp directories
os.makedirs(MEDIA_ROOT, exist_ok=True)

# ============ SECURITY SETTINGS ============
# Content Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# HTTPS Settings (only in production)
SECURE_SSL_REDIRECT = IS_PRODUCTION
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie Security
SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_SECURE = IS_PRODUCTION
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript for AJAX
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# HSTS
SECURE_HSTS_SECONDS = 31536000 if IS_PRODUCTION else 0  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_PRODUCTION
SECURE_HSTS_PRELOAD = IS_PRODUCTION

# CORS settings
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS.copy()
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============ LOGGING ============
# Create logs directory
LOG_DIR = BASE_DIR / 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stdout,
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'security.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'converter': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'home': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# More verbose logging in development
if DEBUG:
    LOGGING['loggers']['django']['level'] = 'DEBUG'
    LOGGING['loggers']['django.db.backends'] = {
        'level': 'DEBUG',
        'handlers': ['console'],
        'propagate': False,
    }

# ============ CACHE ============
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Use Redis in production if available
REDIS_URL = os.getenv('REDIS_URL')
if REDIS_URL and IS_PRODUCTION:
    CACHES['default'] = {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }

# ============ EMAIL ============
if IS_PRODUCTION:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@pdfconverterpro.com')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ============ FILE UPLOAD SECURITY ============
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_FILE_TYPES = [
    'pdf', 'doc', 'docx', 'xls', 'xlsx',
    'jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp'
]

# Secure temp directory
SECURE_TEMP_DIR = BASE_DIR / 'temp_uploads'
os.makedirs(SECURE_TEMP_DIR, exist_ok=True)

# ============ RATE LIMITING ============
AXES_FAILURE_LIMIT = 5 if IS_PRODUCTION else 20  # More lenient in dev
AXES_COOLOFF_TIME = timedelta(minutes=15) if IS_PRODUCTION else timedelta(minutes=2)
AXES_RESET_ON_SUCCESS = True
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_META_PRECEDENCE_ORDER = [
    'X_FORWARDED_FOR',
    'REMOTE_ADDR',
]

# Custom rate limits
UPLOAD_RATE_LIMIT = 10 if IS_PRODUCTION else 50
CONVERSION_RATE_LIMIT = 5 if IS_PRODUCTION else 20

# ============ CUSTOM SETTINGS ============
SITE_NAME = 'PDF Converter Pro'
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000' if DEBUG else 'https://yourdomain.com')
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'support@pdfconverterpro.com')

# Auto-delete uploaded files after X hours
FILE_AUTO_DELETE_HOURS = 24

# File processing timeout (seconds)
FILE_PROCESSING_TIMEOUT = 300  # 5 minutes

# ============ INTERNAL IPS (Debug Toolbar) ============
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Add Render internal IP for debug toolbar
if RENDER_EXTERNAL_HOSTNAME:
    INTERNAL_IPS.append(RENDER_EXTERNAL_HOSTNAME)

# ============ TEST SETTINGS ============
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# ============ DEVELOPMENT SETTINGS ============
if DEBUG:
    # Try to add development-only apps if they're installed
    try:
        import django_extensions
        INSTALLED_APPS.append('django_extensions')
    except ImportError:
        pass  # django_extensions not installed, skip it
    
    try:
        import debug_toolbar
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    except ImportError:
        pass  # debug_toolbar not installed, skip it
    
    # Disable some security features for easier development
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
    
    # Allow all hosts in debug mode
    ALLOWED_HOSTS = ['*']
    
    # Disable SSL redirect in development
    SECURE_SSL_REDIRECT = False
    
    # Show debug toolbar if installed
    try:
        import debug_toolbar
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: True,
        }
    except ImportError:
        pass

# ============ PRODUCTION CHECKS ============
if IS_PRODUCTION:
    # Security checks
    if not SECRET_KEY or SECRET_KEY.startswith('django-insecure-'):
        raise ValueError("Invalid SECRET_KEY in production")
    
    if DEBUG:
        raise ValueError("DEBUG must be False in production")
    
    if not ALLOWED_HOSTS or '*' in ALLOWED_HOSTS:
        raise ValueError("ALLOWED_HOSTS must be properly configured in production")
    
    print(f"✓ Production mode: Serving on {ALLOWED_HOSTS}")
elif IS_LOCAL:
    print(f"✓ Local development mode: DEBUG={DEBUG}")
    print(f"  Access at: http://localhost:8000")
    print(f"  Static files at: {STATIC_ROOT}")