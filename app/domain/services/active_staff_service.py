# app/domain/services/active_staff_service.py
# from app.domain.models import Employee  # Ajusta el import según tu
# estructura real
# from app.domain.database import db_session  # Ajusta el import según tu
# estructura real
from ..repositories import IActiveStaffRepository

class ActiveStaffService:
    """ Servicio para manejar la lógica de negocio relacionada con"""

    def __init__(self, active_staff_repo: IActiveStaffRepository):
        self.active_staff_repo = active_staff_repo

    def get_active_staff_with_line(self, page: int = 1, per_page: int = 20, search_query: str = None):
        empleados, total_count = self.active_staff_repo.get_paginated(page, per_page, search_query)
        resultado = []
        for emp in empleados:
            resultado.append({
                "id": emp.id,
                "nombre": emp.name,
                "apellidos": emp.last_name,
                # "line_name": emp.line_name me falta obtener la línea dónde está el empleado
            })
        
        return {
            "employees": resultado,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page
        }
