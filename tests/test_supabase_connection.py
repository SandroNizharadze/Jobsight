import os
os.environ['USE_SUPABASE'] = 'True'

# Print connection string being used
print("Testing Supabase connection...")

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobsy.settings')
django.setup()

from django.db import connection
from django.conf import settings
import copy

# Create a safe copy of the database settings to print (without password)
safe_db_settings = copy.deepcopy(settings.DATABASES['default'])
if 'PASSWORD' in safe_db_settings:
    safe_db_settings['PASSWORD'] = '********'

print(f"Using connection: {safe_db_settings}")

try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    print('Connection successful!')
except Exception as e:
    print(f'Connection failed: {e}') 