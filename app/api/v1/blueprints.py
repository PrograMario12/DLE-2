"""
app/api/v1/blueprints.py
Centraliza el registro de blueprints e inyecta las dependencias
necesarias.
"""

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
     from .routes.main_routes import main_bp
     from .routes.dashboard_routes import dashboards_bp
     from .routes.settings_routes import settings_bp

     # Inyectar servicios en los módulos de rutas
     main_bp.user_service = user_service
     main_bp.dashboard_service = dashboard_service

     dashboards_bp.dashboard_service = dashboard_service
     settings_bp.user_service = user_service

     # Registrar los blueprints en la aplicación Flask
     app.register_blueprint(main_bp)
     app.register_blueprint(dashboards_bp)
     app.register_blueprint(settings_bp)