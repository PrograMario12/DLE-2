
from app.infra.db.db import get_db
from app.config import settings
from flask import Flask
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

def check_db():
    with app.app_context():
        conn = get_db()
        cur = conn.cursor()
        schema = settings.DB_SCHEMA
        
        print(f"Schema: {schema}")
        
        # 1. Check if position_status table exists
        try:
            cur.execute(sql.SQL("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = %s AND table_name = 'position_status'").format(sql.Identifier(schema)), (schema,))
            columns = cur.fetchall()
            if columns:
                print("Table 'position_status' found. Columns:")
                for col in columns:
                    print(f" - {col[0]} ({col[1]})")
            else:
                print("Table 'position_status' NOT found in information_schema.")
        except Exception as e:
            print(f"Error checking table: {e}")
            conn.rollback()

        # 2. Check relation between Lines in Inyección and Positions
        # Get Inyección lines
        print("\n--- Inyección Lines and their Positions ---")
        cur.execute(sql.SQL("""
            SELECT pl.line_id, pl.name, p.position_id, p.position_name
            FROM {schema}.production_lines pl
            LEFT JOIN {schema}.business_unit bu ON pl.business_unit_fk = bu.bu_id
            LEFT JOIN {schema}.positions p ON pl.line_id = p.line_id
            WHERE LOWER(bu.bu_name) = 'inyección'
            ORDER BY pl.name
            LIMIT 10
        """).format(schema=sql.Identifier(schema)))
        rows = cur.fetchall()
        for r in rows:
            print(f"Line: {r[1]} (ID: {r[0]}) -> Position: {r[3]} (ID: {r[2]})")

        conn.close()

if __name__ == '__main__':
    try:
        check_db()
    except Exception as e:
        print(e)
