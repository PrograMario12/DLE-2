
import psycopg2
from app.config.settings import settings

try:
    uri = settings.SQLALCHEMY_DATABASE_URI
    schema = settings.DB_SCHEMA
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    
    print("\n--- CHECKING DUPLICATES COUNT ---")
    cur.execute(f"""
        SELECT position_id_fk, COUNT(*) 
        FROM {schema}.tbl_sides_of_positions
        GROUP BY position_id_fk
        HAVING COUNT(*) > 1
    """)
    dupes = cur.fetchall()
    print(f"Duplicate Groups: {len(dupes)}")

    print("\n--- CHECKING INYECTORA 20 ID ---")
    q2 = f"""
        SELECT pl.name, p.position_name, s.side_id
        FROM {schema}.production_lines pl
        JOIN {schema}.positions p ON pl.line_id = p.line_id
        JOIN {schema}.tbl_sides_of_positions s ON p.position_id = s.position_id_fk
        WHERE pl.name ILIKE '%Inyec%' 
        AND (p.position_name ILIKE '%20%')
    """
    cur.execute(q2)
    rows2 = cur.fetchall()
    for r in rows2:
        print(f"Inyectora 20 candidate: Line={r[0]}, Pos={r[1]}, SideID={r[2]}")

    conn.close()

except Exception as e:
    print(f"ERROR: {e}")
