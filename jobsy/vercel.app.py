"""
WSGI config for Vercel deployment.
"""

import os
import sys
import subprocess

# Add the project directory to the sys.path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

# Set environment variables for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobsy.vercel_settings')

# Install dependencies
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-minimal.txt"])
except Exception as e:
    print(f"Error installing dependencies from requirements-minimal.txt: {e}")
    try:
        # Fallback to installing only the essential packages
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "Django==3.2.9",
            "django-filter==22.1",
            "djangorestframework==3.14.0",
            "pillow==9.2.0",
            "pg8000==1.29.4",
            "python-dotenv==1.0.1",
            "dj-database-url==2.1.0",
            "whitenoise==6.5.0",
            "gunicorn==21.2.0"
        ])
        print("Successfully installed essential packages")
    except Exception as e2:
        print(f"Error installing essential packages: {e2}")

# Collect static files
try:
    subprocess.check_call([sys.executable, "manage.py", "collectstatic", "--noinput"])
except Exception as e:
    print(f"Error collecting static files: {e}")

# Import and create the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Handler for Vercel serverless function
def handler(request, **kwargs):
    """
    The handler function for Vercel serverless function.
    """
    return application(request, **kwargs)
