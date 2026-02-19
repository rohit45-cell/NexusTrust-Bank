"""
Django settings for nexustrustbank project.
"""

import os
from pathlib import Path
import dj_database_url

# ======================================
# BASE
# ======================================
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-nexustrust-bank-secret-key-2024"
)

DEBUG = True  # Set to False in production

ALLOWED_HOSTS = ["*"]  # For development - restrict in production

# ======================================
# CSRF SETTINGS - FIX FOR CSRF ERROR
# ======================================
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://*.onrender.com',  # For Render deployment
    'http://*.onrender.com',
]

# CSRF Cookie Settings
CSRF_COOKIE_SECURE = False  # Set to True only with HTTPS
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to access CSRF token
CSRF_COOKIE_SAMESITE = 'Lax'  # Helps with cross-site requests
CSRF_USE_SESSIONS = False  # Store CSRF token in cookie (not session)
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'

# ======================================
# SESSION SETTINGS
# ======================================
SESSION_COOKIE_AGE = 900  # 15 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = False  # Set to True with HTTPS
SESSION_COOKIE_SAMESITE = 'Lax'

# ======================================
# APPLICATIONS
# ======================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bankapp',
]

# ======================================
# MIDDLEWARE
# ======================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # This handles CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom middleware (order matters)
    'bankapp.middleware.SecurityHeadersMiddleware',  # Add security headers
    'bankapp.middleware.CSRFTokenMiddleware',       # Ensure CSRF token
    'bankapp.middleware.SessionTimeoutMiddleware',  # Your original middleware
]
ROOT_URLCONF = 'nexustrustbank.urls'

# ======================================
# TEMPLATES
# ======================================
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

WSGI_APPLICATION = 'nexustrustbank.wsgi.application'

# ======================================
# DATABASE
# ======================================
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=False
    )
}

# ======================================
# PASSWORD VALIDATION
# ======================================
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

# ======================================
# INTERNATIONALIZATION
# ======================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ======================================
# STATIC FILES
# ======================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'bankapp' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ======================================
# MEDIA FILES
# ======================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'bankapp' / 'media'

# ======================================
# DEFAULTS
# ======================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ======================================
# CUSTOM USER MODEL
# ======================================
AUTH_USER_MODEL = 'bankapp.User'

# ======================================
# AUTH SETTINGS
# ======================================
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# ======================================
# EMAIL (DEV SAFE)
# ======================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@nexustrustbank.com'

# ======================================
# SECURITY SETTINGS
# ======================================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ======================================
# APP CONSTANTS
# ======================================
CURRENCY = '₹'
