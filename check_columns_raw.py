
import psycopg2
from psycopg2 import sql
# Settings are usually loaded from env or config file. 
# I'll try to guess hardcoded values or read from config file text if possible.
# But better to just import settings if I can.
import sys
import os

sys.path.append(os.getcwd())

try:
    from app.config.settings import settings
    # We need to construct a connection string or params.
    # settings object might have it.
    
    # Assuming DATABASE_URI is in settings (based on typical flask apps)
    # or separate params.
    # Let's inspect settings content first.
    uri = settings.SQLALCHEMY_DATABASE_URI
    schema = settings.DB_SCHEMA
    
    print(f"Connecting to {uri} with schema {schema}")
    
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    
    cur.execute(f"SELECT * FROM {schema}.position_status LIMIT 0")
    cols = [desc[0] for desc in cur.description]
    print("--- COLUMNS ---")
    for c in cols:
        print(c)
    print("--- END COLUMNS ---")
    
    conn.close()

except Exception as e:
    print(f"FAILED: {e}")
