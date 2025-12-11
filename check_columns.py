
from app.main import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # DB_SCHEMA is usually in config
        schema = app.config.get('DB_SCHEMA', 'public')
        print(f"Schema: {schema}")
        
        with db.engine.connect() as conn:
            # Query columns for position_status
            result = conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = '{schema}' 
                AND table_name = 'position_status'
            """))
            
            rows = result.fetchall()
            print("\nColumns in position_status:")
            if not rows:
                print("Table 'position_status' not found or has no columns.")
            for row in rows:
                print(f"- {row[0]}")
                
    except Exception as e:
        print(f"Error: {e}")
