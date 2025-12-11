
import psycopg2
from app.config.settings import settings

try:
    uri = settings.SQLALCHEMY_DATABASE_URI
    schema = settings.DB_SCHEMA
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    
    print(f"--- CHECKING REGISTER SEQUENCE ---")
    # Verify sequence increment
    # Usually sequences are named table_column_seq
    seq_name = f"{schema}.registers_id_register_seq" 
    
    # Try to get sequence info
    cur.execute(f"SELECT * FROM {seq_name}")
    print(f"Sequence State: {cur.fetchone()}")

    # Check definition if possible (pg_sequences)
    cur.execute(f"SELECT * FROM pg_sequences WHERE schemaname = '{schema}' AND sequencename = 'registers_id_register_seq'")
    print(f"Sequence Def: {cur.fetchone()}")

    conn.close()
except Exception as e:
    print(e)
