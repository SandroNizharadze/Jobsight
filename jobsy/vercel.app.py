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

# Install dependencies directly with --no-deps to avoid compilation issues
try:
    print("Installing Django...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-deps", "Django==3.2.9"])
    
    print("Installing djangorestframework...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-deps", "djangorestframework==3.14.0"])
    
    print("Installing pg8000...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-deps", "pg8000==1.29.4"])
    
    print("Installing python-dotenv...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-deps", "python-dotenv==1.0.1"])
    
    print("Installing dj-database-url...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-deps", "dj-database-url==2.1.0"])
    
    print("Installing whitenoise...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-deps", "whitenoise==6.5.0"])
    
    print("Installing gunicorn...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-deps", "gunicorn==21.2.0"])
    
    print("Successfully installed all packages")
except Exception as e:
    print(f"Error installing packages: {e}")

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
