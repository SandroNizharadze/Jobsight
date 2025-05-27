import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobsy.settings')
import django
django.setup()
from django.conf import settings
print("Django settings loaded successfully")
print(f"USE_SUPABASE: {os.environ.get('USE_SUPABASE')}")
print(f"Database ENGINE: {settings.DATABASES['default'].get('ENGINE', 'Not set')}")
print(f"Database HOST: {settings.DATABASES['default'].get('HOST', 'Not set')}")
print(f"Is supabase_settings.py being used? {'Yes' if 'supabase_settings' in str(settings.DATABASES) else 'No'}")
try:
    import django.db
    connection = django.db.connections['default']
    connection.ensure_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        row = cursor.fetchone()
    print(f"Django database connection test: SUCCESS - {row[0]}")
except Exception as e:
    print(f"Django database connection test: FAILED - {e}")
