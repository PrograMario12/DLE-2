from flask import Blueprint, render_template, request, Response
from app.domain.services.active_staff_service import ActiveStaffService
from app.domain.services.production_lines_service import ProductionLinesService
import csv
import io

def register_employees(bp: Blueprint, active_staff_service: ActiveStaffService, production_lines_service: ProductionLinesService) -> None:
    @bp.get("/empleados", endpoint="employees_list")
    def employees_list():
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'id')
        sort_order = request.args.get('sort_order', 'asc')
        line_id = request.args.get('line_id', type=int)
        
        # Obtiene todos los empleados y su línea
        data = active_staff_service.get_active_staff_with_line(
            page=page, 
            per_page=20, 
            search_query=search,
            sort_by=sort_by,
            sort_order=sort_order,
            line_id=line_id
        )
        
        # Obtener líneas para el filtro
        lines = production_lines_service.get_all_zones()
        
        return render_template(
            "employees_list.html", 
            employees=data['employees'],
            pagination=data,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            line_id=line_id,
            lines=lines
        )

    @bp.get("/empleados/exportar", endpoint="export_employees_csv")
    def export_employees_csv():
        employees = active_staff_service.get_all_active_for_export()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['ID', 'Nombre', 'Apellidos', 'Línea', 'Hora Entrada', 'Activo'])
        
        for emp in employees:
            writer.writerow([
                emp.id, 
                emp.name, 
                emp.last_name, 
                emp.line_name if emp.line_name else "N/A",
                emp.entry_time if emp.entry_time else "N/A",
                "Sí" if emp.is_active else "No"
            ])
        
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=empleados_activos.csv"}
        )
