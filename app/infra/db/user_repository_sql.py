"""
src/infra/db/user_repository_sql.py
Implementación del repositorio de usuarios usando Psycopg2.
"""
from .db import get_db
from app.domain.entities.user import User, StationInfo
from app.domain.repositories.user_repository import IUserRepository
from typing import List, Dict, Any, Optional
from psycopg2 import sql

class UserRepositorySQL(IUserRepository):
    """Implementación del repositorio con Psycopg2."""

    def __init__(self, schema: str):
        self.schema = schema

    def _get_cursor(self):
        # Esta es la línea clave: ahora llama a la función que maneja 'g'
        return get_db().cursor()

    def find_user_by_card_number(self, card_number: int) -> Optional[User]:
        query = """
        SELECT id_empleado, nombre_empleado, apellidos_empleado
        FROM {schema}.table_empleados_tarjeta
        WHERE numero_tarjeta = %s \
        LIMIT 1 \
        """

        query = sql.SQL(query).format(schema=sql.Identifier(self.schema))
        cursor = self._get_cursor()
        # Usamos parámetros para prevenir inyección SQL
        cursor.execute(query, (card_number,))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return None

        return User(id=result[0], name=result[1], last_name=result[2])

    def get_line_name_by_id(self, line_id: int) -> Optional[str]:
        """
        Obtiene el nombre completo de una línea en la tabla 'zones' dado su ID.

        Args:
            line_id (int): El identificador único de la línea.

        Returns:
            Optional[str]: El nombre completo de la línea en formato 'type_zone name',
            o None si no se encuentra la línea.
        """
        # Consulta SQL para obtener el nombre completo de la línea
        query = sql.SQL("""
            SELECT TRIM(CONCAT_WS(' ', type_zone, name)) AS full_name
            FROM {schema}.zones
            WHERE line_id = %s
            LIMIT 1
            """).format(schema=sql.Identifier(self.schema))

        # Obtiene un cursor para ejecutar la consulta
        cur = self._get_cursor()
        try:
            # Ejecuta la consulta con el ID de la línea como parámetro
            cur.execute(query, (line_id,))
            row = cur.fetchone()
            # Retorna el nombre completo si existe, de lo contrario retorna None
            return row[0] if row and row[0] else None
        finally:
            # Asegura que el cursor se cierre después de la operación
            cur.close()

    def get_station_cards_for_line(self, line_id: int) -> list[dict[str, any]]:
        """
        Obtiene y procesa los datos de las estaciones para una línea específica,
        uniendo las tablas por sus IDs de clave foránea.
        """

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
            JOIN {schema}.tbl_sides_of_positions s
                 ON p.position_id = s.position_id_fk
            LEFT JOIN employees_working ew
                 ON s.side_id = ew.position_id_fk
            WHERE p.line_id = %s
            ORDER BY p.position_name, s.side_title;
                        """).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query, (line_id,))
        results = cursor.fetchall()
        cursor.close()

        print("Los resultados son: ", results)

        # Agrupar los resultados por estación en Python
        cards = {}
        # El nombre de la variable aquí también cambia para mayor claridad
        for station_name, side_id, side_title, capacity, operators in results:
            if station_name not in cards:
                cards[station_name] = {
                    "position_name": station_name,
                    "status": True,
                    "sides": []
                }

            cards[station_name]["sides"].append({
                "side_id": side_id,                 # <-- clave necesaria para el frontend
                "side_title": side_title,           # <-- útil para mostrar
                "name_side": side_title,            # <-- compatibilidad con código existente
                "employee_capacity": capacity,
                "employees_working": operators
            })

        return list(cards.values())

    def get_last_register_type(self, card_number: int) -> str:
        """
        Determina si la próxima acción del usuario debe ser 'Entrada' o 'Salida'.
        Se basa en la lógica original: si el último registro no tiene hora de salida,
        la próxima acción es una 'Salida'. En cualquier otro caso, es una 'Entrada'.
        """
        query = sql.SQL("""
                        SELECT exit_hour
                        FROM {schema}.registers
                        WHERE id_employee = %s
                        ORDER BY id_register DESC
                        LIMIT 1
                        """)

        formatted_query = query.format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(formatted_query, (card_number,))
        result = cursor.fetchone()
        cursor.close()

        # Si se encontró un registro y su 'exit_hour' es NULA,
        # significa que el usuario está "dentro", por lo que la próxima acción es 'Exit'.
        if result and result[0] is None:
            return 'Exit'

        # Si no hay registros, o si el último registro ya tiene una 'exit_hour',
        # significa que el usuario está "fuera", por lo que la próxima acción es 'Entry'.
        return 'Entry'

    def get_last_station_for_user(self, user_id: int) -> Optional[str]:
        # Implementación aquí
        pass

    def get_all_lines(self) -> list[dict]:
        """Implementación que obtiene todas las líneas de la tabla de zonas."""
        query = sql.SQL(
            "SELECT line_id, type_zone || ' ' || name as line_name "
            "FROM {schema}.zones ORDER BY line_id"
        )
        formatted_query = query.format(
            schema=sql.Identifier(self.schema)
        )
        cursor = self._get_cursor()
        cursor.execute(formatted_query)
        # Convertimos la tupla de resultados en una lista de diccionarios
        lines = [
            {"id": row[0], "name": row[1]} for row in cursor.fetchall()
        ]
        cursor.close()
        return lines

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Encuentra un usuario por su id_empleado."""
        query = """
                SELECT id_empleado, nombre_empleado, apellidos_empleado
                FROM table_empleados_tarjeta
                WHERE id_empleado = %s \
                LIMIT 1 \
                """
        cursor = self._get_cursor()
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return None

        return User(id=result[0], name=result[1], last_name=result[2])

    def get_all_lines_summary(self) -> list[dict]:
        """
        Obtiene un resumen de todas las líneas con sus operadores y capacidad.
        (Esta es la nueva implementación para lines_dashboards.html)
        """
        # Esta consulta es un ejemplo y necesitará ser ajustada a tu lógica de negocio exacta
        query = sql.SQL("""
                        SELECT z.line_id,
                               z.type_zone || ' ' || z.name  as line_name,
                               COUNT(DISTINCT r.id_employee) as current_operators,
                               SUM(s.employee_capacity)      as total_capacity
                        FROM {schema}.zones z
            LEFT JOIN {schema}.positions p
                        ON z.line_id = p.line_id
                            LEFT JOIN {schema}.tbl_sides_of_positions s ON p.position_id = s.position_id_fk
                            LEFT JOIN {schema}.registers r ON s.side_id = r.position_id_fk AND r.exit_hour IS NULL
                        GROUP BY z.line_id, line_name
                        ORDER BY z.line_id;
                        """).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        lines = [
            {"id": row[0], "name": row[1], "operators": row[2],
             "capacity": row[3]}
            for row in results
        ]
        return lines

    def get_active_operators(self, station_id: int) -> list:
        """
        Obtiene los nombres de los empleados activos en una estación específica.
        """
        query = sql.SQL("""
                        SELECT e.nombre_empleado, e.apellidos_empleado
                        FROM {schema}.registers r
            JOIN {schema}.table_empleados_tarjeta e
                        ON r.id_employee = e.numero_tarjeta
                        WHERE r.position_id_fk = %s AND r.exit_hour IS NULL;
                        """).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query, (station_id,))
        results = cursor.fetchall()
        cursor.close()

        # Devolvemos una lista simple de nombres, como en el original
        return [f"{row[0]} {row[1]}" for row in results]
