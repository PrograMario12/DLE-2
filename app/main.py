"""
app/main.py
Fábrica de la aplicación Flask.
"""

from flask import Flask
from .config.settings import settings  # Importa la configuración de la aplicación
from .containers import Container
from .extensions import login_manager  # Importa el manejador de inicio de sesión
from .api.v1.blueprints import register_all_blueprints  # Función para registrar blueprints
from .infra.db import db as db_setup  # Inicialización de la base de datos
from .infra.http.auth import register_login

def create_app(config=settings):
    """
    Fábrica de la aplicación Flask.

    Args:
        config: Configuración de la aplicación Flask. Por defecto, se
        utiliza la configuración definida en `settings`.

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

    container = Container()
    container.config.db_schema.from_value(
        app.config.get('DB_SCHEMA', 'public'))

    app.container = container

    register_login(app, container.user_service())

    # Registra todos los blueprints en la aplicación
    register_all_blueprints(
        app,
        container.user_service(),
        container.dashboard_service(),
        None,
        container.active_staff_service()
    )

    return app  # Devuelve la instancia de la aplicación Flask
