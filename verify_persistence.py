
from app.main import create_app
from app.infra.db.production_lines_repository_sql import ProductionLineRepositorySQL
from app.config.settings import settings

app = create_app()

with app.app_context():
    try:
        schema = settings.DB_SCHEMA
        repo = ProductionLineRepositorySQL(schema)
        
        target_pid = 170 # Known Inyectora
        
        print(f"--- TEST: Setting PID {target_pid} to TRUE ---")
        repo.update_position_status(target_pid, True)
        
        print("--- VERIFYING ---")
        cursor = repo._get_cursor()
        cursor.execute(f"SELECT is_active FROM {schema}.position_status WHERE position_id_fk = %s", (target_pid,))
        row = cursor.fetchone()
        print(f"Readback: {row}")
        if row and row[0] is True:
            print("SUCCESS: True persisted.")
        else:
            print("FAIL: True not persisted.")
        
        print(f"--- TEST: Setting PID {target_pid} to FALSE ---")
        repo.update_position_status(target_pid, False)
        
        cursor.execute(f"SELECT is_active FROM {schema}.position_status WHERE position_id_fk = %s", (target_pid,))
        row = cursor.fetchone()
        print(f"Readback: {row}")
        if row and row[0] is False:
            print("SUCCESS: False persisted.")
        else:
            print("FAIL: False not persisted.")
        
    except Exception as e:
        print(f"ERROR: {e}")
