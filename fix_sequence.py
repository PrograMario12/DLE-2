
import psycopg2
from app.config.settings import settings

try:
    uri = settings.SQLALCHEMY_DATABASE_URI
    schema = settings.DB_SCHEMA
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    
    print(f"--- FIXING SEQUENCE FOR {schema}.positions ---")
    
    # 1. Get Max ID
    cur.execute(f"SELECT MAX(position_id) FROM {schema}.positions")
    max_id = cur.fetchone()[0]
    print(f"Current MAX position_id: {max_id}")
    
    if max_id is None:
        max_id = 0
        
    next_id = max_id + 1
    
    # 2. Reset Sequence
    # Assuming sequence name is positions_position_id_seq inside schema or public?
    # Usually <schema>.<table_name>_<column_name>_seq
    seq_name = f"{schema}.positions_position_id_seq"
    
    print(f"Attempting to reset sequence {seq_name} to {next_id}...")
    
    # Check if sequence exists first (optional but safer)
    # Or just try executing setval
    try:
        cur.execute(f"SELECT setval('{seq_name}', %s)", (next_id,))
        print("Sequence reset successfully.")
    except Exception as e:
        print(f"Error resetting {seq_name}: {e}")
        conn.rollback()
        
        # Try alternate naming if schema logic is different
        print("Trying alternate sequence name format...")
        seq_name_alt = "positions_position_id_seq" # Public schema or just name
        cur.execute(f"SELECT setval('{seq_name_alt}', %s)", (next_id,))
        print("Sequence reset successfully (Attempt 2).")

    conn.commit()
    conn.close()
    
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
