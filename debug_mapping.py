
import psycopg2
from app.config.settings import settings

try:
    uri = settings.SQLALCHEMY_DATABASE_URI
    schema = settings.DB_SCHEMA
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    

    print(f"--- COLUMNS TYPE ---")
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = '{schema}' 
        AND table_name = 'position_status'
    """)
    rows = cur.fetchall()
    for r in rows:
        print(f"{r[0]}: {r[1]}")
    
    # Original logic fixed
    cur.execute(f"SELECT position_id_fk, is_active FROM {schema}.position_status WHERE position_id_fk = 170")
    st = cur.fetchone()
    print(f"Status in DB for 170: {st}")

    conn.close()
except Exception as e:
    print(e)
