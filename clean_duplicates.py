
import psycopg2
from app.config.settings import settings

try:
    uri = settings.SQLALCHEMY_DATABASE_URI
    schema = settings.DB_SCHEMA
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    
    print(f"--- CLEANING DUPLICATE SIDES ---")
    print(f"Schema: {schema}")

    # Check duplicates internal
    cur.execute(f"""
        SELECT position_id_fk, COUNT(*) 
        FROM {schema}.tbl_sides_of_positions
        GROUP BY position_id_fk
        HAVING COUNT(*) > 1
    """)
    dupes = cur.fetchall()
    print(f"Duplicates seen internally: {len(dupes)} groups")
    if dupes:
        print(f"Example: Group {dupes[0][0]} has {dupes[0][1]} rows")

    # 3. Ultimate Weapon: Delete by CTID
    # This keeps exactly one row per position (the oldest one physically)
    q_ctid = f"""
        DELETE FROM {schema}.tbl_sides_of_positions
        WHERE ctid NOT IN (
            SELECT MIN(ctid)
            FROM {schema}.tbl_sides_of_positions
            GROUP BY position_id_fk
        )
    """
    # Debug count
    cur.execute(f"SELECT COUNT(*) FROM {schema}.tbl_sides_of_positions")
    total_before = cur.fetchone()[0]
    print(f"Total rows before: {total_before}")
    
    cur.execute(q_ctid)
    deleted_ctid = cur.rowcount
    conn.commit() # Ensure commit happens immediately
    print(f"Deleted {deleted_ctid} records using CTID.")
    
    print(f"--- CLEANING DUPLICATE POSITIONS ---")
    
    cur.execute(f"SELECT COUNT(*) FROM {schema}.positions")
    pos_before = cur.fetchone()[0]
    print(f"Positions before: {pos_before}")

    q_pos = f"""
        DELETE FROM {schema}.positions
        WHERE ctid NOT IN (
            SELECT MIN(ctid)
            FROM {schema}.positions
            GROUP BY line_id, position_name
        )
    """
    cur.execute(q_pos)
    deleted_pos = cur.rowcount
    conn.commit()
    print(f"Deleted {deleted_pos} duplicate POSITIONS.")

    cur.execute(f"SELECT COUNT(*) FROM {schema}.positions")
    pos_after = cur.fetchone()[0]
    print(f"Positions after: {pos_after}")

    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
