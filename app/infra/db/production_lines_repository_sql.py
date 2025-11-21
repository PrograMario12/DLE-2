# app/infra/db/zones_repository_sql.py
from abc import ABC
from psycopg2 import sql

from app.domain.repositories.IProductionLinesRepository import (
    IProductionLinesRepository)
from .db import get_db


def _get_cursor():
    return get_db().cursor()


class ProductionLineRepository(IProductionLinesRepository, ABC):
    def __init__(self, schema: str):
        self.schema = schema

    def get_all_zones(self):
        cursor = get_db().cursor()
        cursor.execute(f"SELECT * FROM {self.schema}.zones")
        results = cursor.fetchall()
        cursor.close()
        return results


    def get_line_name_by_id(self, line_id: int) -> Optional[str]:
        """
        Obtiene el nombre completo de una línea en la tabla 'zones' dado su ID.
        """
        query = sql.SQL("""
                        SELECT TRIM(CONCAT_WS(' ', type_zone, name)) AS full_name
                        FROM {schema}.zones
                        WHERE line_id = %s
                        LIMIT 1
                        """).format(schema=sql.Identifier(self.schema))

        cur = _get_cursor()
        try:
            cur.execute(query, (line_id,))
            row = cur.fetchone()
            return row[0] if row and row[0] else None
        finally:
            cur.close()