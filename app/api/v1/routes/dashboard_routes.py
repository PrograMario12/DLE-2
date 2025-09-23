from flask import Blueprint, render_template, request, jsonify
from app.domain.services.dashboard_service import DashboardService

# El blueprint ahora tiene el prefijo /dashboards
dashboards_bp = Blueprint('dashboards', __name__, url_prefix='/dashboards')

# Placeholder para el servicio que será inyectado
dashboard_service: DashboardService


@dashboards_bp.route('/lines')
def show_lines_dashboard():
    """
    Renderiza la página principal que muestra el resumen de todas las
    líneas.
    (Reemplaza la antigua ruta /visualizaciones_lines)
    """

    lines_data = dashboards_bp.dashboard_service.get_lines_summary()
    return render_template('lines_dashboards.html', lines=lines_data)

@dashboards_bp.route('/stations')
def show_stations_dashboard():
    """
    Renderiza el dashboard detallado para una sola línea de estaciones.
    (Reemplaza la antigua ruta /dashboard_estaciones)
    """
    line_id = request.args.get('line', type=int)
    if not line_id:
        # Manejar el caso en que no se proporciona una línea
        return "Error: Se requiere un ID de línea.", 400

    # Llama al servicio para obtener los datos de las estaciones de esa línea
    station_data = dashboards_bp.dashboard_service.get_station_details_for_line(line_id)
    print("La data es: ", station_data)
    return render_template('stations_dashboards.html', **station_data)


@dashboards_bp.route('/api/operators')
def get_active_operators():
    """
    Endpoint de API que devuelve los operadores activos para una estación.
    (Reemplaza la antigua ruta /get_operators_actives)
    """
    station_id = request.args.get('id', type=int)
    if not station_id:
        return jsonify({"error": "Se requiere un ID de estación."}), 400

    # Llama al servicio para obtener los datos y los devuelve como JSON
    operators = dashboards_bp.dashboard_service.get_active_operators_for_station(station_id)
    return jsonify(operators)