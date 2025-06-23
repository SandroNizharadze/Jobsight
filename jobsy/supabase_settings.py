import os
import dj_database_url
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if running in main module to prevent duplicate logs during imports
def log_setting(message):
    if __name__ == '__main__':
        print(message)

# Supabase Database Configuration using connection string
# Try pooler connection first (IPv4 compatible), fall back to direct connection
connection_string = os.environ.get('SUPABASE_POOLER_CONNECTION_STRING', 
                                 os.environ.get('SUPABASE_CONNECTION_STRING'))

# Only log in debug mode when directly invoked
if __name__ == '__main__':
    host_info = connection_string.split('@')[1].split('/')[0] if connection_string else 'None'
    log_setting("*** Supabase Settings ***")
    log_setting(f"SUPABASE_POOLER_CONNECTION_STRING exists: {'Yes' if os.environ.get('SUPABASE_POOLER_CONNECTION_STRING') else 'No'}")
    log_setting(f"SUPABASE_CONNECTION_STRING exists: {'Yes' if os.environ.get('SUPABASE_CONNECTION_STRING') else 'No'}")
    log_setting(f"Connection string host: {host_info}")
    log_setting("************************")

if not connection_string:
    raise ValueError("No Supabase connection string found in environment variables. Please set SUPABASE_POOLER_CONNECTION_STRING or SUPABASE_CONNECTION_STRING.")

DATABASES = {
    'default': dj_database_url.parse(connection_string, conn_max_age=600, ssl_require=True)
} 