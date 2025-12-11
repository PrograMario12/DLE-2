
import psycopg2
from app.config.settings import settings

try:
    uri = settings.SQLALCHEMY_DATABASE_URI
    schema = settings.DB_SCHEMA
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    
    print(f"--- FIXING REGISTER SEQUENCE ---")
    seq_name = f"{schema}.registers_id_register_seq" 
    
    # 1. Reset INCREMENT to 1
    # ALTER SEQUENCE schema.seq INCREMENT BY 1;
    print("Setting INCREMENT to 1...")
    cur.execute(f"ALTER SEQUENCE {seq_name} INCREMENT BY 1")
    
    # 2. Sync value to max(id)
    print("Syncing sequence value...")
    cur.execute(f"SELECT MAX(id_register) FROM {schema}.registers")
    max_id = cur.fetchone()[0] or 0
    print(f"Max ID is {max_id}. Setting sequence to {max_id + 1}")
    
    cur.execute(f"SELECT setval('{seq_name}', %s)", (max_id + 1,))
    
    conn.commit()
    print("Sequence fixed.")
    
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
