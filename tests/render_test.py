import os
import sys
import psycopg2

# Print environment variables (without sensitive values)
print("Environment variables:")
for key in sorted(os.environ.keys()):
    if "PASSWORD" in key or "SECRET" in key or "KEY" in key:
        print(f"{key}=********")
    else:
        print(f"{key}={os.environ.get(key)}")

# Check if Supabase environment variables are set
print("\nChecking Supabase configuration:")
use_supabase = os.environ.get('USE_SUPABASE') == 'True'
pooler_conn_string = os.environ.get('SUPABASE_POOLER_CONNECTION_STRING')
direct_conn_string = os.environ.get('SUPABASE_CONNECTION_STRING')

print(f"USE_SUPABASE: {use_supabase}")
print(f"SUPABASE_POOLER_CONNECTION_STRING: {'Set' if pooler_conn_string else 'Not set'}")
print(f"SUPABASE_CONNECTION_STRING: {'Set' if direct_conn_string else 'Not set'}")

# Try to connect to the database
print("\nTesting database connection:")
try:
    # Use pooler connection string if available, otherwise use direct connection string
    conn_string = pooler_conn_string or direct_conn_string
    
    if not conn_string:
        print("No connection string available. Please set SUPABASE_POOLER_CONNECTION_STRING or SUPABASE_CONNECTION_STRING.")
        sys.exit(1)
    
    # Connect to the database
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    
    # Test the connection
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"Successfully connected to the database. Version: {version[0]}")
    
    # Close the connection
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Failed to connect to the database: {e}")
    sys.exit(1) 