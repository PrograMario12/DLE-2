
import psycopg2
from app.config.settings import settings

try:
    uri = settings.SQLALCHEMY_DATABASE_URI
    schema = settings.DB_SCHEMA
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    
    print(f"--- CHECKING DUPLICATE POSITIONS ---")
    cur.execute(f"""
        SELECT line_id, COUNT(*) 
        FROM {schema}.positions
        GROUP BY line_id
        HAVING COUNT(*) > 1
    """)
    rows = cur.fetchall()
    if not rows:
        print("No duplicate POSITIONS found.")
    else:
        print(f"Found {len(rows)} lines with multiple positions:")
        for r in rows:
            print(f"Line {r[0]}: {r[1]} positions")
            
            # Detail
            cur.execute(f"SELECT * FROM {schema}.positions WHERE line_id = %s", (r[0],))
            pos = cur.fetchall()
            for p in pos:
                print(f"  - {p}")

    print(f"\n--- CHECKING DUPLICATE SIDES AGAIN ---")
    cur.execute(f"""
        SELECT position_id_fk, COUNT(*) 
        FROM {schema}.tbl_sides_of_positions
        GROUP BY position_id_fk
        HAVING COUNT(*) > 1
    """)
    rows = cur.fetchall()
    if not rows:
        print("No duplicate SIDES found.")
    else:
        print(f"Found {len(rows)} positions with multiple sides:")
        for r in rows:
            print(f"Position {r[0]}: {r[1]} sides")

    conn.close()
except Exception as e:
    print(e)
