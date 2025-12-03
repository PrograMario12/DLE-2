"""
Registra todos los blueprints en la aplicación Flask, asociando los
servicios necesarios a cada uno.
app/api/v1/blueprints.py
"""

# Importa la función para crear el blueprint principal
from .routes.main import create_main_bp
# Importa el blueprint de dashboards
from .routes.dashboard_routes import dashboards_bp
# Importa la función para crear el blueprint de configuración
from .routes.settings_routes import create_settings_bp

def register_all_blueprints(app, user_service, dashboard_service,
                            station_service, active_staff_service, production_lines_service):
    """
    Registra todos los blueprints en la aplicación Flask.

    Este método asocia servicios específicos a los blueprints y los registra
    en la aplicación Flask proporcionada.

    Args:
        production_lines_service: Servicio para manejar la lógica de las
        líneas de producción.
        app (Flask): La instancia de la aplicación Flask donde se
        registrarán los blueprints.
        user_service: Servicio para manejar la lógica relacionada con
        usuarios.
        dashboard_service: Servicio para manejar la lógica de los
        dashboards.
        station_service: Servicio para manejar la lógica de las
            estaciones (opcional).
        active_staff_service: Servicio para manejar la lógica del
        personal activo.

    Returns:
        None
    """
    # Asocia el servicio de dashboard al blueprint de dashboards
    dashboards_bp.dashboard_service = dashboard_service

    # Registra el blueprint principal, pasando los servicios necesarios
    app.register_blueprint(create_main_bp(
        user_service,
        dashboard_service,
        station_service,
        active_staff_service,
        production_lines_service
    ))

    # Registra el blueprint de dashboards
    app.register_blueprint(dashboards_bp)

    # Registra el blueprint de configuración
    app.register_blueprint(create_settings_bp(user_service))
