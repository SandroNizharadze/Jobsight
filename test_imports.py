import sys
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobsy.settings')
django.setup()

print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    import core
    print("Successfully imported core")
    
    from core import models
    print("Successfully imported core.models")
    
    # Try importing from core.models.__init__
    from core.models import JobListing
    print("Successfully imported JobListing from core.models")
    
    # Try direct import from the module file
    try:
        from core.models.job import JobListing as JobListing2
        print("Successfully imported JobListing directly from core.models.job")
    except ImportError as e:
        print(f"Error importing from core.models.job: {e}")
    
except ImportError as e:
    print(f"Import error: {e}") 