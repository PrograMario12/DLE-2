# app/domain/services/active_staff_service.py
# from app.domain.models import Employee  # Ajusta el import según tu
# estructura real
# from app.domain.database import db_session  # Ajusta el import según tu
# estructura real
from ..repositories import IActiveStaffRepository
from datetime import datetime

class ActiveStaffService:
    """ Servicio para manejar la lógica de negocio relacionada con"""

    def __init__(self, active_staff_repo: IActiveStaffRepository):
        self.active_staff_repo = active_staff_repo

    def get_active_staff_with_line(self, page: int = 1, per_page: int = 20, search_query: str = None,
                                   sort_by: str = 'id', sort_order: str = 'asc', line_id: int = None):
        empleados, total_count = self.active_staff_repo.get_paginated(
            page, per_page, search_query, sort_by, sort_order, line_id
        )
        resultado = []
        now = datetime.now()
        
        for emp in empleados:
            duration_str = "N/A"
            if emp.entry_time:
                # Ensure entry_time is timezone-naive or aware as needed. Assuming naive for simplicity or matching system time.
                # If entry_time is a time object, we combine with today, if datetime we use directly.
                # Psycopg2 usually returns datetime or time. Let's handle datetime.
                if isinstance(emp.entry_time, datetime):
                    delta = now - emp.entry_time
                    hours, remainder = divmod(delta.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    duration_str = f"{hours}h {minutes}m"
            
            resultado.append({
                "id": emp.id,
                "nombre": emp.name,
                "apellidos": emp.last_name,
                "line_name": emp.line_name,
                "duration": duration_str,
                "is_active": emp.is_active
            })
        
        return {
            "employees": resultado,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page
        }

    def get_all_active_for_export(self):
        return self.active_staff_repo.get_all_active()
