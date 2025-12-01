from abc import ABC

from .db import get_db
from app.domain.entities.active_staff import ActiveStaff
from app.domain.repositories.IActiveStaffRepository import IActiveStaffRepository
from typing import List, Optional, Tuple
from psycopg2 import sql

class ActiveStaffRepositorySQL(IActiveStaffRepository, ABC):
    """Implementación del repositorio de personal activo con Psycopg2."""

    def __init__(self, schema: str):
        self.schema = schema

    @staticmethod
    def _get_cursor():
        return get_db().cursor()

    def get_paginated(self, page: int, per_page: int, search_query: Optional[str] = None) -> Tuple[List[ActiveStaff], int]:
        offset = (page - 1) * per_page
        
        # Base query conditions
        where_clause = sql.SQL("WHERE r.exit_hour IS NULL")
        params = []
        
        if search_query:
            where_clause = sql.SQL("{} AND (CAST(e.id_empleado AS TEXT) ILIKE %s)").format(where_clause)
            params.append(f"%{search_query}%")

        # Main query
        query = sql.SQL("""
            SELECT DISTINCT e.id_empleado,
                   e.nombre_empleado,
                   e.apellidos_empleado,
                   TRUE as is_active
            FROM {schema}.registers r
            JOIN {schema}.table_empleados_tarjeta e
            ON r.id_employee = e.numero_tarjeta
            {where}
            ORDER BY e.id_empleado
            LIMIT %s OFFSET %s
        """).format(
            schema=sql.Identifier(self.schema),
            where=where_clause
        )
        
        # Count query
        count_query = sql.SQL("""
            SELECT COUNT(DISTINCT e.id_empleado)
            FROM {schema}.registers r
            JOIN {schema}.table_empleados_tarjeta e
            ON r.id_employee = e.numero_tarjeta
            {where}
        """).format(
            schema=sql.Identifier(self.schema),
            where=where_clause
        )

        cursor = self._get_cursor()
        
        # Execute count
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Execute main query
        cursor.execute(query, params + [per_page, offset])
        results = cursor.fetchall()
        cursor.close()

        employees = [
            ActiveStaff(
                id=row[0],
                name=row[1],
                last_name=row[2],
                is_active=row[3]
            )
            for row in results
        ]
        
        return employees, total_count
