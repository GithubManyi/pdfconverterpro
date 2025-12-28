"""
Django settings for pdfconverterpro project.
Simple version for Render free tier.
"""

import os
from pathlib import Path
import dj_database_url

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ============ BASIC SETTINGS ============
# For Render free tier, detect production by checking for DATABASE_URL
IS_RENDER = os.getenv('RENDER') is not None
IS_PRODUCTION = IS_RENDER  # On Render = production

# Secret Key - Render provides this in production
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise ValueError("SECRET_KEY must be set in Render environment variables")
    else:
        # Local development fallback
        SECRET_KEY = 'django-insecure-dev-key-change-in-production'

# DEBUG mode - Always False on Render for security
if IS_PRODUCTION:
    DEBUG = False
else:
    # For local development, allow DEBUG=True
    DEBUG = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']

# ============ ALLOWED HOSTS ============
ALLOWED_HOSTS = []

# Render provides this automatically
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# For local development
if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '[::1]'])

# ============ CSRF TRUSTED ORIGINS ============
CSRF_TRUSTED_ORIGINS = []
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ])

# ============ APPLICATIONS ============
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
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ============ DATABASE ============
# Default SQLite for local development
# SIMPLE DATABASE SETTINGS THAT WORK
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# On Render, they provide PostgreSQL
if os.getenv('RENDER'):
    # Render provides PostgreSQL
    import dj_database_url
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
# ============ PASSWORD VALIDATION ============
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============ INTERNATIONALIZATION ============
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============ STATIC FILES ============
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


# ============ MEDIA FILES ============
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Create directories
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(STATIC_ROOT, exist_ok=True)

# ============ SECURITY ============
if IS_PRODUCTION:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SECURE_SSL_REDIRECT = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ============ DEFAULT PRIMARY KEY ============
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============ CUSTOM SETTINGS ============
SITE_NAME = 'PDF Converter Pro'
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000' if DEBUG else f'https://{RENDER_EXTERNAL_HOSTNAME}')
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'support@pdfconverterpro.com')

# ============ STARTUP MESSAGE ============
print("=" * 50)
print(f"Starting {SITE_NAME}")
print(f"Production: {IS_PRODUCTION}")
print(f"Debug Mode: {DEBUG}")
print(f"Allowed Hosts: {ALLOWED_HOSTS}")
print("=" * 50)