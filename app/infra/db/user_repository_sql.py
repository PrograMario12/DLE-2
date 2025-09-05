from typing import Optional
from flask import g
from app.domain.entities.user import User, StationInfo
from app.domain.repositories.user_repository import IUserRepository
from typing import List, Dict, Any, Optional


class UserRepositorySQL(IUserRepository):
    """Implementación del repositorio con Psycopg2."""

    def _get_cursor(self):
        return g.db.cursor()

    def find_user_by_card_number(self, card_number: int) -> Optional[User]:
        query = """
                SELECT id_empleado, nombre_empleado, apellidos_empleado
                FROM table_empleados_tarjeta
                WHERE numero_tarjeta = %s \
                LIMIT 1 \
                """
        cursor = self._get_cursor()
        # Usamos parámetros para prevenir inyección SQL
        cursor.execute(query, (card_number,))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return None

        return User(id=result[0], name=result[1], last_name=result[2])

    def get_line_name_by_id(self, line_id: int) -> Optional[str]:
        query = "SELECT type_zone || ' ' || name FROM zones WHERE line_id = %s"
        cursor = self._get_cursor()
        cursor.execute(query, (line_id,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    def get_station_cards_for_line(self, line_id: int) -> List[Dict[str, Any]]:
        """
        Implementación de la consulta compleja para obtener los datos de las tarjetas.
        Esta es una adaptación de tu lógica original.
        """
        # Esta consulta es compleja y puede necesitar ajustes finos
        # según tu esquema exacto, pero la estructura es la correcta.
        query = """
                SELECT p.position_id, \
                       p.position_name, \
                       p.status, \
                       s.side_id, \
                       s.name_side, \
                       s.employee_capacity, \
                       (SELECT COUNT(*) FROM registers r WHERE r.position_id_fk = s.side_id) as employees_working
                FROM positions p
                         JOIN tbl_sides_of_positions tsp ON p.position_id = tsp.position_id_fk
                         JOIN sides s ON tsp.side_id = s.side_id
                WHERE p.line_id_fk = %s
                ORDER BY p.position_name, s.name_side; \
                """
        cursor = self._get_cursor()
        cursor.execute(query, (line_id,))
        results = cursor.fetchall()
        cursor.close()

        # Agrupar resultados por posición para construir la estructura de tarjetas
        cards = {}
        for row in results:
            pos_id, pos_name, status, side_id, side_name, capacity, working = row
            if pos_id not in cards:
                cards[pos_id] = {
                    "position_name": pos_name,
                    "status": status,
                    "sides": []
                }
            cards[pos_id]["sides"].append({
                "side_id": side_id,
                "name_side": side_name,
                "employee_capacity": capacity,
                "employees_working": working
            })

        return list(cards.values())

    def get_last_register_type(self, user_id: int) -> Optional[str]:
        # Implementación aquí
        pass

    def get_last_station_for_user(self, user_id: int) -> Optional[str]:
        # Implementación aquí
        pass

    def get_all_lines(self) -> list[dict]:
        """Implementación que obtiene todas las líneas de la tabla de zonas."""
        query = "SELECT line_id, type_zone || ' ' || name as line_name FROM zones ORDER BY line_id"
        cursor = self._get_cursor()
        cursor.execute(query)
        # Convertimos la tupla de resultados en una lista de diccionarios
        lines = [
            {"id": row[0], "name": row[1]} for row in cursor.fetchall()
        ]
        cursor.close()
        return lines