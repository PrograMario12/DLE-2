
import psycopg2
from app.config.settings import settings

try:
    uri = settings.SQLALCHEMY_DATABASE_URI
    schema = settings.DB_SCHEMA
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    
    print(f"--- COLUMNS tbl_sides_of_positions ---")
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = '{schema}' 
        AND table_name = 'tbl_sides_of_positions'
    """)
    rows = cur.fetchall()
    for r in rows:
        print(f"{r[0]}: {r[1]}")

    conn.close()
except Exception as e:
    print(e)
