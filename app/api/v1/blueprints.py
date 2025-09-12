"""
app/api/v1/blueprints.py
Centraliza el registro de blueprints e inyecta las dependencias
necesarias.
"""

from .routes.main import create_main_bp  # Importa el blueprint principal
from .routes.dashboard_routes import dashboards_bp  # Importa el blueprint de tableros
from .routes.settings_routes import settings_bp  # Importa el blueprint de configuración

def register_all_blueprints(app, user_service, dashboard_service):
    """
    Centraliza el registro de blueprints e inyecta las dependencias
    necesarias.

    Args:
     app (Flask): La instancia de la aplicación Flask donde se
     registrarán los blueprints.
     user_service (UserService): Servicio de usuario que será
     inyectado en los blueprints.
     dashboard_service (DashboardService): Servicio de tablero que
     será inyectado en los blueprints.

    Funcionalidad:
     - Importa los blueprints principales de la aplicación.
     - Inyecta las dependencias requeridas en cada blueprint.
     - Registra los blueprints en la aplicación Flask.

    Blueprints registrados:
     - main_bp: Rutas principales de la aplicación.
     - dashboards_bp: Rutas relacionadas con los tableros.
     - settings_bp: Rutas para la configuración de línea y estación.
    """

    dashboards_bp.dashboard_service = dashboard_service  # Asigna el
    # servicio de tablero al blueprint de tableros
    settings_bp.user_service = user_service  # Asigna el servicio de
    # usuario al blueprint de configuración

    # Registrar los blueprints en la aplicación Flask
    app.register_blueprint(create_main_bp(user_service, dashboard_service))  # Registra el
    # blueprint
    # principal
    app.register_blueprint(dashboards_bp)  # Registra el blueprint de
    # tableros
    app.register_blueprint(settings_bp)  # Registra el blueprint de
    # configuración