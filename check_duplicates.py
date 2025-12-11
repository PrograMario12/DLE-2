
import psycopg2
from app.config.settings import settings

try:
    uri = settings.SQLALCHEMY_DATABASE_URI
    schema = settings.DB_SCHEMA
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    
    print(f"--- CHECKING DUPLICATE SIDES ---")
    cur.execute(f"""
        SELECT position_id_fk, COUNT(*) 
        FROM {schema}.tbl_sides_of_positions
        GROUP BY position_id_fk
        HAVING COUNT(*) > 1
    """)
    rows = cur.fetchall()
    if not rows:
        print("No duplicates found by count.")
    else:
        print(f"Found {len(rows)} positions with multiple sides:")
        for r in rows:
            print(f"Position {r[0]}: {r[1]} sides")
            
            # Detail
            cur.execute(f"SELECT * FROM {schema}.tbl_sides_of_positions WHERE position_id_fk = %s", (r[0],))
            sides = cur.fetchall()
            for s in sides:
                print(f"  - {s}")

    conn.close()
except Exception as e:
    print(e)
