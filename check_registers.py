
import psycopg2
from app.config.settings import settings

try:
    uri = settings.SQLALCHEMY_DATABASE_URI
    schema = settings.DB_SCHEMA
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    
    print(f"--- COLUMNS FOR {schema}.registers ---")
    cur.execute(f"""
        SELECT column_name, ordinal_position 
        FROM information_schema.columns 
        WHERE table_schema = '{schema}' AND table_name = 'registers' 
        ORDER BY ordinal_position
    """)
    rows = cur.fetchall()
    for r in rows:
        print(r)

    print("\n--- LAST 5 REGISTERS ---")
    cur.execute(f"SELECT * FROM {schema}.registers ORDER BY id_register DESC LIMIT 5")
    regs = cur.fetchall()
    for r in regs:
        print(r)

    conn.close()
except Exception as e:
    print(e)
