"""
COMS - Construction Operations Management System
Core Settings Configuration
"""
import os
from pathlib import Path
from datetime import timedelta
import environ

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

# Read .env file if it exists
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(env_file)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-CHANGE-THIS-IN-PRODUCTION')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '0.0.0.0'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # JWT token blacklist
    'corsheaders',
    'django_bootstrap5',
    'django_htmx',
    'drf_spectacular',
    'django_filters',  # Django filter for DRF
    'axes',  # Login attempt tracking
    
    # Local apps
    'apps.core',
    'apps.authentication',
    'apps.projects',
    'apps.ledger',
    'apps.workers',
    'apps.consultants',
    'apps.clients',
    'apps.suppliers',
    'apps.bq',
    'apps.documents',
    'apps.media',
    'apps.approvals',
    'apps.workflows',
    'apps.dashboards',
    'apps.valuations',
    'apps.site_operations',
    'apps.portfolio',
    'apps.cashflow',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',  # Login attempt tracking (must be after AuthenticationMiddleware)
    'django_htmx.middleware.HtmxMiddleware',  # HTMX support
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgresql://coms_user:coms_pass@localhost:5432/coms_db')
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'  # Kenya timezone
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# Authentication URLs
LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/login/'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.authentication.authentication.JWTCookieAuthentication',  # Custom cookie-based JWT
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Fallback to header
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
from apps.authentication.constants import JWT_ACCESS_MINUTES, JWT_REFRESH_DAYS

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=JWT_ACCESS_MINUTES),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=JWT_REFRESH_DAYS),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_COOKIE': 'access_token',  # Cookie name for access token
    'AUTH_COOKIE_REFRESH': 'refresh_token',  # Cookie name for refresh token
    'AUTH_COOKIE_SECURE': not DEBUG,  # Set True in production
    'AUTH_COOKIE_HTTP_ONLY': True,  # Protect against XSS
    'AUTH_COOKIE_SAMESITE': 'Lax',  # CSRF protection
}

# CORS Settings
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:3000',
    'http://localhost:8000',
])

# Security Settings (Production)
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True if not DEBUG else False)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True if not DEBUG else False)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True if not DEBUG else False)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = env('X_FRAME_OPTIONS', default='SAMEORIGIN')

# Session Configuration
SESSION_COOKIE_AGE = 120  # 2 minutes in seconds
SESSION_SAVE_EVERY_REQUEST = True  # Update session on every request to track activity
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Clear session when browser closes

# Email Configuration
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

# Celery Configuration
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'coms.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# DRF Spectacular Settings (API Documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'COMS API',
    'DESCRIPTION': 'Construction Operations Management System API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Django Axes Configuration (Login Attack Detection)
# Import constants from authentication app
from apps.authentication.constants import (
    AXES_FAILURE_LIMIT,
    AXES_COOLOFF_TIME,
)

AXES_FAILURE_LIMIT = AXES_FAILURE_LIMIT  # Maximum failed login attempts
AXES_COOLOFF_TIME = AXES_COOLOFF_TIME  # Lockout time in minutes
AXES_RESET_ON_SUCCESS = True  # Reset attempts counter on successful login
AXES_LOCKOUT_TEMPLATE = None  # Use default or create custom template
AXES_ENABLE_ACCESS_FAILURE_LOG = True  # Log access failures
AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT = False
AXES_VERBOSE = True  # Detailed logging
AXES_LOCKOUT_PARAMETERS = [['username', 'ip_address'], ['username'], ['ip_address']]  # Lock by combination

# Authentication backend with Axes
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # AxesStandaloneBackend should be first
    'django.contrib.auth.backends.ModelBackend',
]
