from .settings import *
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'placeholder-secret-key-do-not-use-in-production')

# SECURITY WARNING: update this with your production domain
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'jobsy-uoul.onrender.com,localhost,127.0.0.1,jobsight.ge,www.jobsight.ge').split(',')

# Database - Production always uses Supabase
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'jobsy_db'),
        'USER': os.environ.get('DB_USER', 'admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'db_password_placeholder'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Use DATABASE_URL if provided (for Render deployment)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES["default"] = dj_database_url.parse(DATABASE_URL)

# Always use Supabase in production
USE_SUPABASE = True
from .supabase_settings import DATABASES
print("Production environment: Using Supabase database")

# Enable S3 storage in production
USE_S3 = os.environ.get('USE_S3', 'True') == 'True'

if USE_S3:
    from .s3_settings import *
else:
    # Static files
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True 