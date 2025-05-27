import os
import sys
import psycopg2
import time

def test_connection():
    # Hardcoded connection string for testing
    conn_string = "postgres://***REMOVED***:Ss%40598282954@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"
    
    print(f"Testing connection to: {conn_string.split('@')[1].split('/')[0]}")
    
    # Try to connect
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print("SUCCESS: Database connection works!")
        return True
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {str(e)}")
        return False

if __name__ == "__main__":
    # Try connection multiple times with delay
    for i in range(3):
        print(f"Connection attempt {i+1}...")
        if test_connection():
            sys.exit(0)
        time.sleep(5)
    
    sys.exit(1) 