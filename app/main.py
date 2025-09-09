"""
app/main.py
Fábrica de la aplicación Flask.
"""

from flask import Flask
from .config.settings import settings
from .extensions import login_manager
from .api.v1.blueprints import register_all_blueprints
from .domain.services.user_service import UserService
from .domain.services.dashboard_service import DashboardService
from .infra.db.user_repository_sql import UserRepositorySQL
from .infra.db import db as db_setup  # Importamos nuestro nuevo módulo

def create_app(config=settings):
    """
    Fábrica de la aplicación Flask.

    Args:
        config: Configuración de la aplicación Flask. Por defecto, se utiliza
                la configuración definida en `settings`.

    Returns:
        Flask: Una instancia de la aplicación Flask configurada.
    """
    app = Flask(__name__)
    app.config.from_object(config)

    # Inicializa la base de datos con la configuración de la aplicación
    db_setup.init_app(app)

    # Configura el manejador de inicio de sesión
    login_manager.init_app(app)

    # Obtiene el esquema de la base de datos desde la configuración
    schema = app.config.get('DB_SCHEMA', 'public')

    # Crea una instancia del repositorio de usuarios con el esquema configurado
    user_repo = UserRepositorySQL(schema=schema)

    # Crea instancias de los servicios de usuario y tablero
    user_service = UserService(user_repo)
    dashboard_service = DashboardService(user_repo)

    @login_manager.user_loader
    def load_user(user_id: str):
        """
        Carga un usuario desde la base de datos dado su ID.

        Args:
            user_id (str): El ID del usuario a cargar.

        Returns:
            User: Una instancia del usuario cargado desde la base de datos,
                  o None si no se encuentra.
        """
        with app.app_context():
            # Usa la instancia de user_repo para buscar al usuario por su ID
            return user_repo.find_by_id(int(user_id))

    # Registra todos los blueprints en la aplicación
    register_all_blueprints(app, user_service, dashboard_service)

    return app
