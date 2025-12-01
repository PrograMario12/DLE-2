"""
src/infra/db/user_repository_sql.py
Implementación del repositorio de usuarios usando Psycopg2.
"""

from .db import get_db
from app.domain.entities.user import User
from app.domain.repositories.IUserRepository import IUserRepository
from typing import Optional
from psycopg2 import sql

class UserRepositorySQL(IUserRepository):
    """Implementación del repositorio de usuarios con Psycopg2."""

    def __init__(self, schema: str):
        self.schema = schema

    def _get_cursor(self):
        return get_db().cursor()

    def find_user_by_card_number(self, card_number: int) -> Optional[User]:
        query = sql.SQL(
            "SELECT id_empleado, nombre_empleado, apellidos_empleado, numero_tarjeta "
            "FROM {schema}.table_empleados_tarjeta "
            "WHERE numero_tarjeta = %s "
            "LIMIT 1"
        ).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query, (card_number,))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return None

        return User(id=result[0], name=result[1], last_name=result[2],
                    numero_tarjeta=result[3])

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Encuentra un usuario por su id_empleado."""
        query = sql.SQL(
            "SELECT id_empleado, nombre_empleado, apellidos_empleado "
            "FROM {schema}.table_empleados_tarjeta "
            "WHERE id_empleado = %s "
            "LIMIT 1"
        ).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return None

        return User(id=result[0], name=result[1], last_name=result[2])
