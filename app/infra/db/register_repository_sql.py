from abc import ABC
from typing import Optional
from psycopg2 import sql
from datetime import datetime
from app.domain.repositories.IRegisterRepository import IRegisterRepository
from .db import get_db

class RegisterRepositorySQL(IRegisterRepository, ABC):
    """Implementación del repositorio de registros con Psycopg2."""

    def __init__(self, schema: str):
        self.schema = schema

    def _get_cursor(self):
        return get_db().cursor()

    def get_last_register_type(self, card_number: int) -> str:
        query = sql.SQL("""
            SELECT CASE
                WHEN exit_hour IS NULL THEN 'Exit'
                ELSE 'Entry'
                END AS register_type
            FROM {schema}.registers
            WHERE id_employee = %s
            ORDER BY id_register DESC
            LIMIT 1
        """).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query, (card_number,))
        result = cursor.fetchone()
        cursor.close()

        print(f"DEBUG_REPO: get_last_register_type for {card_number}. Result raw: {result}")

        if not result:
            print("DEBUG_REPO: No result -> Returning 'Entry'")
            return 'Entry'

        print(f"DEBUG_REPO: Returning {result[0]}")
        return result[0]

    def get_last_station_for_user(self, user_id: int) -> Optional[dict]:
        query = sql.SQL("""
            SELECT p.position_name, pl.name, pl.type_zone
            FROM {schema}.registers r
            JOIN {schema}.positions p ON r.position_id_fk = p.position_id
            JOIN {schema}.production_lines pl ON p.line_id = pl.line_id
            WHERE r.id_employee = %s
            ORDER BY r.id_register DESC
            LIMIT 1
        """).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return None
        
        # Concatenar type_zone y name para el nombre completo de la línea
        line_name = f"{result[2]} {result[1]}".strip()
        
        return {
            "station_name": result[0],
            "line_name": line_name
        }

    def register_entry_or_assignment(self, user_id: int, side_id: int) -> None:
        cur = self._get_cursor()

        try:
            # 1) Buscar registro abierto (usuario actualmente trabajando)
            q_open = sql.SQL("""
                SELECT id_register
                FROM {schema}.registers
                WHERE id_employee = %s AND exit_hour IS NULL
                ORDER BY id_register DESC
                LIMIT 1
            """).format(schema=sql.Identifier(self.schema))
            cur.execute(q_open, (user_id,))
            open_row = cur.fetchone()
            print(f"DEBUG_REPO: Open register search for user {user_id}. Found: {open_row}")

            now_time = datetime.now().strftime("%H:%M:%S")
            today_date = datetime.now().strftime("%Y-%m-%d")

            # Si hay un registro abierto, lo cerramos primero
            if open_row:
                q_close = sql.SQL("""
                    UPDATE {schema}.registers
                    SET exit_hour = %s WHERE id_register = %s
                """).format(schema=sql.Identifier(self.schema))
                cur.execute(q_close, (now_time, open_row[0]))
                # NO hacemos return aquí para permitir el "Clock In" inmediato en la nueva estación
                print(f"DEBUG_REPO: Closed previous register {open_row[0]}")

            # Si se proporcionó un side_id válido, creamos el NUEVO registro de entrada
            if side_id > 0:
                q_side = sql.SQL("""
                    SELECT p.line_id, p.position_id
                    FROM {schema}.tbl_sides_of_positions s
                    JOIN {schema}.positions p ON p.position_id = s.position_id_fk
                    WHERE s.side_id = %s
                    LIMIT 1
                """).format(schema=sql.Identifier(self.schema))
                cur.execute(q_side, (side_id,))
                side_row = cur.fetchone()
                
                if not side_row:
                    raise ValueError(f"Side con ID {side_id} no encontrado")

                line_id, position_id = side_row[0], side_row[1]

                q_insert = sql.SQL("""
                    INSERT INTO {schema}.registers
                        (id_employee, date_register, entry_hour, line_id_fk, position_id_fk, side_id_fk)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_register
                """).format(schema=sql.Identifier(self.schema))
                cur.execute(q_insert, (user_id, today_date, now_time, line_id, position_id, side_id))
                new_id = cur.fetchone()[0]
                print(f"DEBUG_REPO: Inserted new register with ID: {new_id}")
            
            cur.connection.commit()

        except Exception:
            cur.connection.rollback()
            raise
        finally:
            cur.close()

    def logout_active_users_in_line(self, line_id: int) -> int:
        cur = self._get_cursor()
        try:
            now_time = datetime.now().strftime("%H:%M:%S")
            
            # Update all active registers (exit_hour IS NULL) for the given line
            query = sql.SQL("""
                UPDATE {schema}.registers
                SET exit_hour = %s
                WHERE line_id_fk = %s AND exit_hour IS NULL
            """).format(schema=sql.Identifier(self.schema))
            
            cur.execute(query, (now_time, line_id))
            affected_rows = cur.rowcount
            cur.connection.commit()
            
            print(f"DEBUG_REPO: Logout general line {line_id}. Affected rows: {affected_rows}")
            return affected_rows
            
        except Exception as e:
            cur.connection.rollback()
            print(f"ERROR_REPO: logout_active_users_in_line failed: {e}")
            raise
        finally:
            cur.close()
