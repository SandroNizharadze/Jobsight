"""
Development settings for Jobsy project.
This file contains settings that are only used during development.
"""

from .settings import *
import os

# Use file-based SQLite database for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Skip migrations that are PostgreSQL-specific
MIGRATION_MODULES = {
    'core': 'core.dev_migrations',
}

print("Using file-based SQLite database for development") 