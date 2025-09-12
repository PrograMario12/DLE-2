"""
app/main.py
Fábrica de la aplicación Flask.
"""

from flask import Flask
from .config.settings import settings  # Importa la configuración de la aplicación
from .extensions import login_manager  # Importa el manejador de inicio de sesión
from .api.v1.blueprints import register_all_blueprints  # Función para registrar blueprints
from .domain.services.user_service import UserService  # Servicio de lógica de negocio para usuarios
from .domain.services.dashboard_service import DashboardService  # Servicio de lógica de negocio para tableros
from .infra.db.user_repository_sql import UserRepositorySQL  # Repositorio SQL para usuarios
from .infra.db import db as db_setup  # Inicialización de la base de datos
from .infra.http.auth import register_login


def create_app(config=settings):
    """
    Fábrica de la aplicación Flask.

    Args:
        config: Configuración de la aplicación Flask. Por defecto, se utiliza
                la configuración definida en `settings`.

    Returns:
        Flask: Una instancia de la aplicación Flask configurada.
    """
    app = Flask(__name__)  # Crea una instancia de Flask
    app.config.from_object(config)  # Configura la aplicación con el
    # objeto de configuración

    # Inicializa la base de datos con la configuración de la aplicación
    db_setup.init_app(app)

    # Configura el manejador de inicio de sesión
    login_manager.init_app(app)

    # Obtiene el esquema de la base de datos desde la configuración
    schema = app.config.get('DB_SCHEMA', 'public')  # Por defecto, usa el esquema 'public'

    # Crea una instancia del repositorio de usuarios con el esquema configurado
    user_repo = UserRepositorySQL(schema=schema)

    # Crea instancias de los servicios de usuario y tablero
    user_service = UserService(user_repo)  # Servicio de usuarios con el repositorio inyectado
    dashboard_service = DashboardService(user_repo)  # Servicio de tableros con el repositorio inyectado

    register_login(app, user_service)

    # Registra todos los blueprints en la aplicación
    register_all_blueprints(app, user_service, dashboard_service)

    return app  # Devuelve la instancia de la aplicación Flask
