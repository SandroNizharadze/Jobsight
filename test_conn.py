import psycopg2
conn_string = "postgres://***REMOVED***:Ss%40598282954@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"
try:
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
