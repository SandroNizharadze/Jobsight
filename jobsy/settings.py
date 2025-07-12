# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

import os
from pathlib import Path
from dotenv import load_dotenv

# Try to import dj_database_url, but don't fail if it's not available
try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# Load environment variables from .env file if it exists
load_dotenv()

# Function to control logging output to prevent duplication
def log_setting(message):
    # Only print during direct invocation with DEBUG on, not during imports
    if __name__ == '__main__':
        print(message)

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'placeholder-secret-key-for-development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Update allowed hosts
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.jobsight.ge', '.render.com', 'testserver', '192.168.0.100']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'social_django',
    'import_export',
    'rangefilter',
    'storages',
    'ckeditor',
    'ckeditor_uploader',
    'core',
    'django_ckeditor_5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.EmailVerificationMiddleware',
]

ROOT_URLCONF = 'jobsy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.employer_premium_status',
                'core.context_processors.language_attributes',
                'core.context_processors.employer_notifications',
                'core.context_processors.candidate_notifications',
                'core.context_processors.rejection_reasons',
            ],
        },
    },
]

WSGI_APPLICATION = 'jobsy.wsgi.application'

# Database - Default to local PostgreSQL for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'jobsy_db'),
        'USER': os.environ.get('DB_USER', 'admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Use DATABASE_URL if provided (for Render deployment)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and dj_database_url:
    DATABASES["default"] = dj_database_url.parse(DATABASE_URL)

# Use Supabase only if explicitly enabled and we're not in development
# For development, default to False to use local PostgreSQL
# For production (Render), this will be True to use Supabase
USE_SUPABASE = os.environ.get('USE_SUPABASE', 'False') == 'True'
if USE_SUPABASE:
    from .supabase_settings import DATABASES
    log_setting("Using Supabase database")
else:
    log_setting("Using local PostgreSQL database")
    
# Fallback to SQLite if PostgreSQL connection fails
USE_SQLITE_FALLBACK = False
if USE_SQLITE_FALLBACK:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    log_setting("Using SQLite database (fallback mode)")

# Authentication
AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_OAUTH2_SECRET', '')
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'job_list'
LOGOUT_REDIRECT_URL = 'job_list'
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'prompt': 'select_account',
}
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']

# Explicitly set redirect protocol based on DEBUG setting
SOCIAL_AUTH_REDIRECT_IS_HTTPS = not DEBUG

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 4,
        }
    },
]

# Internationalization
LANGUAGE_CODE = 'ka'
TIME_ZONE = 'Asia/Tbilisi'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('ka', 'ქართული'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# S3 Settings - Apply when USE_S3 is True
# Only print configuration information when running directly (not via django imports)
USE_S3 = os.environ.get('USE_S3', 'False') == 'True'
log_setting(f"USE_S3 value from environment: {os.environ.get('USE_S3', 'NOT SET')}")

# Define media locations for consistency
PRIVATE_MEDIA_LOCATION = 'media/private'

# Media files - Only use local storage if S3 is disabled
if not USE_S3:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    log_setting("Using LOCAL media storage")
else:
    # Import S3 settings but don't set MEDIA_URL or MEDIA_ROOT as they'll come from s3_settings.py
    log_setting("S3 settings are being imported")
    try:
        from .s3_settings import *
        # Only print config status once
        if DEBUG and __name__ == '__main__':
            print("S3 Configuration Status:")
            print(f"AWS_ACCESS_KEY_ID: {'Set' if 'AWS_ACCESS_KEY_ID' in locals() else 'Not set'}")
            print(f"AWS_SECRET_ACCESS_KEY: {'Set' if 'AWS_SECRET_ACCESS_KEY' in locals() else 'Not set'}")
            print(f"AWS_STORAGE_BUCKET_NAME: {locals().get('AWS_STORAGE_BUCKET_NAME', 'Not set')}")
            print(f"AWS_S3_REGION_NAME: {locals().get('AWS_S3_REGION_NAME', 'Not set')}")
    except ImportError:
        log_setting("Error importing S3 settings, falling back to local storage")
        MEDIA_URL = '/media/'
        MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'core': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'social': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'social_core': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'social_django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Email Configuration
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@jobsight.ge')

# For development/testing, you can use the console backend
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CKEditor 5 Settings
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|', 
            'bold', 'italic', 'strikethrough', 'underline', 'removeFormat', '|',
            'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|',
            'bulletedList', 'numberedList', 'todoList', '|',
            'outdent', 'indent', '|',
            'blockQuote', 'insertTable', 'mediaEmbed', 'link', 'imageUpload', '|',
            'alignment', '|',
            'undo', 'redo'
        ],
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'}
            ]
        },
        'language': {
            'ui': 'en',
            'content': 'ka',
            'textPartLanguage': [
                { 'title': 'Georgian', 'languageCode': 'ka' },
                { 'title': 'English', 'languageCode': 'en' }
            ]
        },
        'ckfinder': {
            'uploadUrl': '/ckeditor5/upload/'
        },
        'css': {
            'all': ['/static/css/ckeditor5-custom.css']
        },
        'extraPlugins': ['Font', 'Image', 'Table', 'MediaEmbed', 'Alignment', 'List'],
        'font': {
            'supportAllValues': True
        },
        'fontSize': {
            'options': [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
            'supportAllValues': True
        },
        'enterMode': 2,  # CKEDITOR.ENTER_BR
        'entities': False,
        'entities_greek': False,
        'entities_latin': False,
        'entities_processNumerical': False,
        'entities_additional': '',
        'forcePasteAsPlainText': False,  # Changed to False to preserve Georgian text
        'allowedContent': True,  # Allow all content
        'disableNativeSpellChecker': False,
        'disableObjectResizing': False,
        'contentsCss': ['/static/css/ckeditor5-contents.css'],
        'extraAllowedContent': '*[*]{*}(*)',  # Allow all tags, attributes, styles
        'pasteFilter': None,  # Disable paste filtering
        'forceEnterMode': True,  # Force the enter mode
        'autoParagraph': False,  # Disable auto paragraph
        'basicEntities': False,
        'fillEmptyBlocks': False,
        'tabSpaces': 0,
        'fullPage': False,
        'ignoreEmptyParagraph': True,
    }
}

# CKEditor 5 upload folder
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
CKEDITOR_5_UPLOAD_PATH = 'uploads/ckeditor/'

# Standard CKEditor configuration
CKEDITOR_UPLOAD_PATH = 'uploads/ckeditor/'
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_IMAGE_BACKEND = 'pillow'

# Silence the CKEditor security warning
SILENCED_SYSTEM_CHECKS = ["ckeditor.W001"]

CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_Full': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Flash', 'Table', 'HorizontalRule'],
            ['TextColor', 'BGColor'],
            ['Smiley', 'SpecialChar'], ['Source'],
        ],
        'toolbar': 'Full',
        'height': 400,
        'width': '100%',
        'filebrowserWindowHeight': 725,
        'filebrowserWindowWidth': 940,
        'toolbarCanCollapse': True,
        'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage',
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    },
} 