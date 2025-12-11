from abc import ABC
from typing import Optional, List, Dict, Any
from psycopg2 import sql
from app.domain.repositories.IProductionLinesRepository import IProductionLinesRepository
from .db import get_db

class ProductionLineRepositorySQL(IProductionLinesRepository, ABC):
    """Implementación del repositorio de líneas de producción con Psycopg2."""

    def __init__(self, schema: str):
        self.schema = schema

    def _get_cursor(self):
        return get_db().cursor()

    def get_all_lines(self) -> list[dict]:
        query = sql.SQL(
            "SELECT line_id, name, type_zone, bu.bu_name "
            "FROM {schema}.production_lines pl "
            "LEFT JOIN {schema}.business_unit bu ON pl.business_unit_fk = bu.bu_id "
            "ORDER BY bu.bu_name, "
            "CASE WHEN LOWER(name) = 'afe' THEN 1 ELSE 0 END ASC, "
            "CAST(SUBSTRING(name FROM '^[0-9]+') AS INTEGER) ASC, "
            "name ASC"
        ).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query)
        lines = [
            {
                "id": row[0],
                "name": row[1],
                "type_zone": row[2],
                "group": row[3],       # metalizado / inyección / ensamble
            }
            for row in cursor.fetchall()
        ]
        cursor.close()
        return lines

    def get_all_lines_summary(self) -> list[dict]:
        query = sql.SQL("""
            SELECT pl.line_id,
                   pl.type_zone || ' ' || pl.name  as line_name,
                   COUNT(DISTINCT r.id_employee) as current_operators,
                   SUM(s.employee_capacity)      as total_capacity
            FROM {schema}.production_lines pl
            LEFT JOIN {schema}.positions p ON pl.line_id = p.line_id
            LEFT JOIN {schema}.tbl_sides_of_positions s ON p.position_id = s.position_id_fk
            LEFT JOIN {schema}.registers r ON s.side_id = r.position_id_fk AND r.exit_hour IS NULL
            GROUP BY pl.line_id, line_name
            ORDER BY pl.line_id;
        """).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        return [
            {"id": row[0], "name": row[1], "operators": row[2], "capacity": row[3]}
            for row in results
        ]

    def get_station_cards_for_line(self, line_id: int) -> List[Dict[str, Any]]:
        query = sql.SQL("""
            WITH employees_working AS (
                SELECT r.position_id_fk,
                       COUNT(r.id_register) as employee_count
                FROM {schema}.registers r
                WHERE r.exit_hour IS NULL
                GROUP BY r.position_id_fk
            )
            SELECT p.position_name,
                   s.side_id,
                   s.side_title,
                   s.employee_capacity,
                   COALESCE(ew.employee_count, 0) as operators
            FROM {schema}.positions p
            JOIN {schema}.tbl_sides_of_positions s ON p.position_id = s.position_id_fk
            LEFT JOIN employees_working ew ON s.side_id = ew.position_id_fk
            WHERE p.line_id = %s
            ORDER BY p.position_name, s.side_title;
        """).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query, (line_id,))
        results = cursor.fetchall()
        cursor.close()

        cards = {}
        for station_name, side_id, side_title, capacity, operators in results:
            if station_name not in cards:
                cards[station_name] = {
                    "position_name": station_name,
                    "status": True,
                    "sides": []
                }

            cards[station_name]["sides"].append({
                "side_id": side_id,
                "side_title": side_title,
                "name_side": side_title,
                "employee_capacity": capacity,
                "employees_working": operators
            })

        return list(cards.values())

    def get_active_operators(self, station_id: int) -> list:
        query = sql.SQL("""
            SELECT e.nombre_empleado, e.apellidos_empleado
            FROM {schema}.registers r
            JOIN {schema}.table_empleados_tarjeta e ON r.id_employee = e.numero_tarjeta
            WHERE r.position_id_fk = %s AND r.exit_hour IS NULL;
        """).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query, (station_id,))
        results = cursor.fetchall()
        cursor.close()

        return [f"{row[0]} {row[1]}" for row in results]

    def get_line_name_by_id(self, line_id: int) -> Optional[str]:
        query = sql.SQL("""
            SELECT 
                CASE 
                    WHEN LOWER(type_zone) = 'no definida' THEN 
                        CASE WHEN LOWER(name) = 'afe' THEN UPPER(name) ELSE name END
                    ELSE 
                        TRIM(CONCAT_WS(' ', type_zone, CASE WHEN LOWER(name) = 'afe' THEN UPPER(name) ELSE name END))
                END AS full_name
            FROM {schema}.production_lines
            WHERE line_id = %s
            LIMIT 1
        """).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        try:
            cursor.execute(query, (line_id,))
            row = cursor.fetchone()
            return row[0] if row and row[0] else None
        finally:
            cursor.close()

    def get_line_by_id(self, line_id: int) -> Optional[dict]:
        query = sql.SQL("""
            SELECT * FROM {schema}.production_lines
            WHERE line_id = %s
            LIMIT 1
        """).format(schema=sql.Identifier(self.schema))
        
        cursor = self._get_cursor()
        try:
            cursor.execute(query, (line_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_lines_with_position_status(self, group_name: str) -> list[dict]:
        query = sql.SQL("""
            SELECT 
                pl.line_id, 
                pl.name, 
                pl.type_zone,
                p.position_id,
                ps.is_active
            FROM {schema}.production_lines pl
            JOIN {schema}.business_unit bu ON pl.business_unit_fk = bu.bu_id
            JOIN {schema}.positions p ON pl.line_id = p.line_id
            LEFT JOIN {schema}.position_status ps ON p.position_id = ps.position_id_fk
            WHERE LOWER(bu.bu_name) = LOWER(%s)
            ORDER BY 
                CASE WHEN LOWER(pl.name) = 'afe' THEN 1 ELSE 0 END ASC,
                CAST(SUBSTRING(pl.name FROM '^[0-9]+') AS INTEGER) ASC, 
                pl.name ASC
        """).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        try:
            cursor.execute(query, (group_name,))
            rows = cursor.fetchall()
            
            results = []
            for r in rows:
                is_visible = r[4] if r[4] is not None else False 
                
                results.append({
                    "id": r[0],
                    "name": r[1],
                    "type_zone": r[2],
                    "position_id": r[3],
                    "is_visible": is_visible
                })
            return results
        finally:
            cursor.close()

    def update_position_status(self, position_id: int, is_true: bool) -> None:
        cursor = self._get_cursor()
        try:
            # Check if exists
            q_check = sql.SQL("""
                SELECT position_status_id FROM {schema}.position_status 
                WHERE position_id_fk = %s
            """).format(schema=sql.Identifier(self.schema))
            cursor.execute(q_check, (position_id,))
            res = cursor.fetchone()

            if res:
                # Update
                q_update = sql.SQL("""
                    UPDATE {schema}.position_status 
                    SET is_active = %s 
                    WHERE position_id_fk = %s
                """).format(schema=sql.Identifier(self.schema))
                cursor.execute(q_update, (is_true, position_id))
            else:
                # Insert
                q_insert = sql.SQL("""
                    INSERT INTO {schema}.position_status (is_active, position_id_fk)
                    VALUES (%s, %s)
                """).format(schema=sql.Identifier(self.schema))
                cursor.execute(q_insert, (is_true, position_id))
            
            cursor.connection.commit()
        except Exception:
            cursor.connection.rollback()
            raise
        finally:
            cursor.close()
