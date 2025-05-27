import os
import sys

# First check if the RENDER environment variable is set
print(f"RENDER environment variable: {'Set' if os.environ.get('RENDER') else 'Not set'}")

# Test both settings modules
settings_modules = [
    'jobsy.settings',
    'jobsy.render_settings'
]

for settings_module in settings_modules:
    print(f"\n\nTesting with DJANGO_SETTINGS_MODULE={settings_module}")
    
    # Set the Django settings module
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    
    try:
        # Import Django and initialize
        import django
        django.setup()
        
        # Import settings after Django setup
        from django.conf import settings
        
        print(f"Settings module loaded: {settings.SETTINGS_MODULE}")
        
        # Check database configuration
        print("\nDatabase Configuration:")
        db_config = settings.DATABASES['default']
        for key in ['ENGINE', 'NAME', 'USER', 'HOST', 'PORT']:
            if key in db_config:
                # Don't print PASSWORD for security
                print(f"  {key}: {db_config[key]}")
        
        # Check if using Supabase
        print(f"\nUSE_SUPABASE: {getattr(settings, 'USE_SUPABASE', 'Not set')}")
        
        # Test database connection
        print("\nTesting database connection:")
        try:
            from django.db import connections
            connection = connections['default']
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            print(f"  Connection successful! Result: {result[0]}")
        except Exception as e:
            print(f"  Connection failed: {e}")
    
    except Exception as e:
        print(f"Error loading settings module: {e}")
    
    # Reset Django to test the other settings module
    if 'django.conf' in sys.modules:
        del sys.modules['django.conf']
    if 'django' in sys.modules:
        del sys.modules['django'] 