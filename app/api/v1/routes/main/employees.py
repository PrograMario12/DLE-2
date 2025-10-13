from flask import Blueprint, render_template
from app.domain.services.active_staff_service import ActiveStaffService

def register_employees(bp: Blueprint, active_staff_service: ActiveStaffService) -> None:
    @bp.get("/empleados", endpoint="employees_list")
    def employees_list():
        # Obtiene todos los empleados y su línea (puedes adaptar el método según tu modelo)
        employees = active_staff_service.get_active_staff_with_line()
        return render_template("employees_list.html", employees=employees)
