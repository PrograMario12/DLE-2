
import psycopg2
from app.config.settings import settings

try:
    uri = settings.SQLALCHEMY_DATABASE_URI
    schema = settings.DB_SCHEMA
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    
    print(f"--- DUMPING BUSINESS UNITS (repr) ---")
    cur.execute(f"SELECT bu_id, bu_name FROM {schema}.business_unit")
    bus = cur.fetchall()
    for b in bus:
        print(f"{b[0]}: {repr(b[1])}")
        
    print("\n--- TESTING QUERY ---")
    # Test query used in repo
    group_name = 'Inyección'
    cur.execute(f"SELECT bu_name FROM {schema}.business_unit WHERE LOWER(bu_name) = LOWER(%s)", (group_name,))
    res = cur.fetchall()
    print(f"Query check for '{group_name}': {res}")

    conn.close()
except Exception as e:
    print(e)
