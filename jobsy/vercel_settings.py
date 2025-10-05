"""
Settings for Vercel deployment.
"""

import os
from .settings import *

# Debug should be False in production
DEBUG = False

# Update allowed hosts
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.vercel.app', '.now.sh', '.jobsight.ge']

# Disable features that require Pillow
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in ['ckeditor', 'ckeditor_uploader', 'django_ckeditor_5']]

# Use DATABASE_URL if provided
import dj_database_url
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    try:
        # Configure to use pg8000 instead of psycopg2
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL, engine='django_postgres')
        }
        # Set the engine to use pg8000
        DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
        DATABASES['default']['OPTIONS'] = {'engine': 'pg8000'}
        print("Using PostgreSQL database with pg8000")
    except Exception as e:
        print(f"Error configuring PostgreSQL: {e}")
        # Fall back to SQLite
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            }
        }
        print("Falling back to SQLite database")
else:
    # If no DATABASE_URL is provided, use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    print("Using SQLite database (no DATABASE_URL provided)")

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Simplified static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email settings - use environment variables
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@jobsight.ge')
