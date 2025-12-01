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

    def get_paginated(self, page: int, per_page: int, search_query: Optional[str] = None, 
                      sort_by: str = 'id', sort_order: str = 'asc', line_id: Optional[int] = None) -> Tuple[List[ActiveStaff], int]:
        offset = (page - 1) * per_page
        
        # Base query conditions
        where_clause = sql.SQL("WHERE 1=1")
        params = []
        
        if search_query:
            search_pattern = f"%{search_query}%"
            where_clause = sql.SQL("{} AND (CAST(e.id_empleado AS TEXT) ILIKE %s OR e.nombre_empleado ILIKE %s OR e.apellidos_empleado ILIKE %s)").format(where_clause)
            params.extend([search_pattern, search_pattern, search_pattern])

        if line_id:
            where_clause = sql.SQL("{} AND r.line_id_fk = %s").format(where_clause)
            params.append(line_id)

        # Sorting
        sort_column = sql.SQL("e.id_empleado")
        if sort_by == 'name':
            sort_column = sql.SQL("e.nombre_empleado")
        elif sort_by == 'line':
            sort_column = sql.SQL("line_name")
        
        sort_direction = sql.SQL("ASC") if sort_order == 'asc' else sql.SQL("DESC")

        # Main query
        query = sql.SQL("""
            SELECT DISTINCT e.id_empleado,
                   e.nombre_empleado,
                   e.apellidos_empleado,
                   CASE WHEN r.entry_hour IS NOT NULL THEN TRUE ELSE FALSE END as is_active,
                   r.entry_hour,
                   TRIM(CONCAT_WS(' ', pl.type_zone, pl.name)) AS line_name
            FROM {schema}.table_empleados_tarjeta e
            LEFT JOIN {schema}.registers r ON e.numero_tarjeta = r.id_employee AND r.exit_hour IS NULL
            LEFT JOIN {schema}.production_lines pl ON r.line_id_fk = pl.line_id
            {where}
            ORDER BY {sort_col} {sort_dir}
            LIMIT %s OFFSET %s
        """).format(
            schema=sql.Identifier(self.schema),
            where=where_clause,
            sort_col=sort_column,
            sort_dir=sort_direction
        )
        
        # Count query
        count_query = sql.SQL("""
            SELECT COUNT(DISTINCT e.id_empleado)
            FROM {schema}.table_empleados_tarjeta e
            LEFT JOIN {schema}.registers r ON e.numero_tarjeta = r.id_employee AND r.exit_hour IS NULL
            LEFT JOIN {schema}.production_lines pl ON r.line_id_fk = pl.line_id
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
                is_active=row[3],
                entry_time=row[4],
                line_name=row[5]
            )
            for row in results
        ]
        
        return employees, total_count

    def get_all_active(self) -> List[ActiveStaff]:
        query = sql.SQL("""
            SELECT DISTINCT e.id_empleado,
                   e.nombre_empleado,
                   e.apellidos_empleado,
                   CASE WHEN r.entry_hour IS NOT NULL THEN TRUE ELSE FALSE END as is_active,
                   r.entry_hour,
                   TRIM(CONCAT_WS(' ', pl.type_zone, pl.name)) AS line_name
            FROM {schema}.table_empleados_tarjeta e
            LEFT JOIN {schema}.registers r ON e.numero_tarjeta = r.id_employee AND r.exit_hour IS NULL
            LEFT JOIN {schema}.production_lines pl ON r.line_id_fk = pl.line_id
            ORDER BY e.id_empleado
        """).format(schema=sql.Identifier(self.schema))

        cursor = self._get_cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        return [
            ActiveStaff(
                id=row[0],
                name=row[1],
                last_name=row[2],
                is_active=row[3],
                entry_time=row[4],
                line_name=row[5]
            )
            for row in results
        ]
