
import psycopg2
from app.config.settings import settings

try:
    uri = settings.SQLALCHEMY_DATABASE_URI
    schema = settings.DB_SCHEMA
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    
    print(f"--- QUERYING {schema}.position_status ---")
    cur.execute(f"SELECT * FROM {schema}.position_status LIMIT 20")
    rows = cur.fetchall()
    if not rows:
        print("Table is empty.")
    for r in rows:
        print(r)
        
    print(f"\n--- QUERYING Registers (Count) ---")
    cur.execute(f"SELECT count(*) FROM {schema}.position_status")
    print(cur.fetchone()[0])

    conn.close()
except Exception as e:
    print(e)
