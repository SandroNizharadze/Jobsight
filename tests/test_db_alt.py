import os
import sys
import psycopg2
import time

def test_connection():
    # First connection string (original pooler)
    conn_string1 = "postgres://***REMOVED***:Ss%40598282954@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"
    
    # Second connection string (direct connection)
    conn_string2 = "postgresql://postgres:Ss%40598282954@db.mvlceicvjchiqnxpygfm.supabase.co:5432/postgres"
    
    for i, conn_string in enumerate([conn_string1, conn_string2]):
        print(f"\nTesting connection string #{i+1}: {conn_string.split('@')[1].split('/')[0]}")
        
        # Try to connect
        try:
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            print(f"SUCCESS: Connection string #{i+1} works!")
        except Exception as e:
            print(f"ERROR with connection string #{i+1}: {str(e)}")

if __name__ == "__main__":
    test_connection() 