from flask import Blueprint, render_template, jsonify, request
from app.domain.services.dashboard_service import DashboardService

# Se crea el Blueprint para las rutas de dashboards
dashboards_bp = Blueprint('dashboards', __name__, url_prefix='/dashboards')

# Se declara el placeholder para el servicio que será inyectado
# en la fábrica de la aplicación (app/main.py)
dashboard_service: DashboardService

@dashboards_bp.route('/')
def index():
    """
    Renderiza la página principal de visualizaciones del dashboard.
    """
    # Esta ruta simplemente sirve el HTML; el frontend se encargará
    # de llamar a los endpoints de API para obtener los datos.
    return render_template('visualizaciones.html')

@dashboards_bp.route('/data')
def get_dashboard_data():
    """
    Endpoint de API para obtener los datos completos del dashboard
    para una línea específica.
    """
    # Se obtiene el ID de la línea desde los argumentos de la URL (ej: /data?line=1)
    line_id = request.args.get('line', default=1, type=int)

    # La ruta llama al servicio para obtener la lógica de negocio
    dashboard_data = dashboard_service.prepare_station_dashboard(line_id)

    # El servicio devuelve un diccionario, que se convierte a JSON
    return jsonify(dashboard_data)

@dashboards_bp.route('/lines')
def get_lines():
    """Endpoint de API que devuelve una lista de todas las líneas disponibles."""
    # Aquí necesitaríamos un método en el servicio/repositorio.
    # Por ahora, simularemos la respuesta que tenías.
    # TODO: Implementar `get_all_lines` en DashboardService y IUserRepository
    lines_data = [
        {"id": 1, "name": "Línea 1"},
        {"id": 2, "name": "Línea 2"},
        {"id": 6, "name": "Inyectora"},
        {"id": 7, "name": "Metalizadora"},
    ]
    return jsonify(lines_data)