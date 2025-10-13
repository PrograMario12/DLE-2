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

    def get_active_staff_with_line(self):
        empleados = self.active_staff_repo.get_all()
        resultado = []
        for emp in empleados:
            resultado.append({
                "id": emp.id,
                "nombre": emp.name
            })
        return resultado
