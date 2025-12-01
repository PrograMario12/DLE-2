from flask import Blueprint, render_template, request
from app.domain.services.active_staff_service import ActiveStaffService

def register_employees(bp: Blueprint, active_staff_service: ActiveStaffService) -> None:
    @bp.get("/empleados", endpoint="employees_list")
    def employees_list():
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        
        # Obtiene todos los empleados y su línea
        data = active_staff_service.get_active_staff_with_line(page=page, search_query=search)
        
        return render_template(
            "employees_list.html", 
            employees=data['employees'],
            pagination=data,
            search=search
        )
