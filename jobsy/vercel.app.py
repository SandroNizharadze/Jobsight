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
    print(f"Error installing dependencies: {e}")

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
