"""
src/infra/db/user_repository_sql.py
Implementación del repositorio de usuarios usando Psycopg2.

todo: Refactorizar este cagadero
"""

from .db import get_db
from app.domain.entities.user import User, StationInfo
from app.domain.repositories.user_repository import IUserRepository
from typing import List, Dict, Any, Optional
from psycopg2 import sql
from datetime import datetime

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
        Obtiene el tipo del último registro (entrada o salida) de un empleado
        basado en su número de tarjeta. Si hay una salida pendiente, la actualiza.
        """
        # Consulta el último registro
        query = sql.SQL("""
                        SELECT id_register, exit_hour
                        FROM {schema}.registers
                        WHERE id_employee = %s
                        ORDER BY id_register DESC
                        LIMIT 1
                        """).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query, (card_number,))
        result = cursor.fetchone()

        if result and result[1] is None:
            # Actualiza el exit_hour con la hora actual
            now_time = datetime.now().strftime("%H:%M:%S")
            update_query = sql.SQL("""
                                   UPDATE {schema}.registers
                                   SET exit_hour = %s WHERE id_register = %s
                                   """).format(
                schema=sql.Identifier(self.schema))
            cursor.execute(update_query, (now_time, result[0]))
            cursor.connection.commit()
            cursor.close()
            return 'Exit'

        cursor.close()
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

    def register_entry_or_assignment(self, user_id: int, side_id: int) -> None:
        """
        Si el usuario tiene un registro abierto, lo cierra (Exit).
        En caso contrario, crea un registro de entrada (Entry) en el side indicado.
        """
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
                                  """).format(
                    schema=sql.Identifier(self.schema))
                cur.execute(q_close, (now_time, open_row[0]))
                cur.connection.commit()
                cur.close()
                return

            # 3) No hay registro abierto: crear Entrada en el side indicado
            q_side = sql.SQL("""
                             SELECT p.line_id, p.position_id
                             FROM {schema}.tbl_sides_of_positions s
                JOIN {schema}.positions p
                             ON p.position_id = s.position_id_fk
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
            cur.execute(q_insert,
                        (user_id, today_date, now_time, line_id, side_id))
            cur.connection.commit()
        except Exception:
            cur.connection.rollback()
            raise
        finally:
            cur.close()

    def get_user_status_for_display(self, card_number: int) -> Optional[
        StationInfo]:
        user = self.find_user_by_card_number(card_number)
        if not user:
            return None

        last_register_type = self.get_last_register_type(card_number)
        station_info = self.get_last_station_for_user(user.id)

        # Puedes ajustar los campos según la definición de StationInfo
        return StationInfo(
            user_name=user.full_name,
            register_type=last_register_type,
            color="employee-ok" if last_register_type == "Entry" else "employee-warning",
            image=f"{user.id}.png",
            station=station_info
        )