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

        if not result:
            return 'Entry'

        if result[0] == 'Entry':
            return 'Entry'
        elif result[0] == 'Exit':
            return 'Exit'
        else:
            return 'Exit'

    def get_last_station_for_user(self, user_id: int) -> Optional[str]:
        query = sql.SQL("""
            SELECT p.position_name
            FROM {schema}.registers r
            JOIN {schema}.positions p ON r.position_id_fk = p.position_id
            WHERE r.id_employee = %s AND r.exit_hour IS NULL
            ORDER BY r.id_register DESC
            LIMIT 1
        """).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return None
        return result[0]

    def register_entry_or_assignment(self, user_id: int, side_id: int) -> None:
        cur = self._get_cursor()

        try:
            # 1) Buscar registro abierto
            q_open = sql.SQL("""
                SELECT id_register
                FROM {schema}.registers
                WHERE id_employee = %s AND exit_hour IS NULL
                ORDER BY id_register DESC
                LIMIT 1
            """).format(schema=sql.Identifier(self.schema))
            cur.execute(q_open, (user_id,))
            open_row = cur.fetchone()

            now_time = datetime.now().strftime("%H:%M:%S")
            today_date = datetime.now().strftime("%Y-%m-%d")

            if open_row:
                # 2) Cerrar registro abierto (Salida)
                q_close = sql.SQL("""
                    UPDATE {schema}.registers
                    SET exit_hour = %s WHERE id_register = %s
                """).format(schema=sql.Identifier(self.schema))
                cur.execute(q_close, (now_time, open_row[0]))
                cur.connection.commit()
                cur.close()
                return

            # 3) No hay registro abierto: crear Entrada en el side indicado
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
                raise ValueError("Side no encontrado")

            line_id, position_id = side_row[0], side_row[1]

            q_insert = sql.SQL("""
                INSERT INTO {schema}.registers
                    (id_employee, date_register, entry_hour, line_id_fk, position_id_fk)
                VALUES (%s, %s, %s, %s, %s)
            """).format(schema=sql.Identifier(self.schema))
            cur.execute(q_insert, (user_id, today_date, now_time, line_id, side_id))
            cur.connection.commit()
        except Exception:
            cur.connection.rollback()
            raise
        finally:
            cur.close()
