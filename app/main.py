"""
app/main.py
Fábrica de la aplicación Flask.
"""

from flask import Flask
from .config.settings import settings  # Importa la configuración de la aplicación
from .containers import Container  # Importa el contenedor de dependencias
from .extensions import login_manager  # Importa el manejador de inicio de sesión
from .api.v1.blueprints import register_all_blueprints  # Función para registrar blueprints
from .infra.db import db as db_setup  # Inicialización de la base de datos
from .infra.http.auth import register_login  # Función para registrar el inicio de sesión

def create_app(config=settings):
    """
    Fábrica de la aplicación Flask.

    Este método crea e inicializa una instancia de la aplicación Flask con
    la configuración proporcionada, inicializa las extensiones necesarias,
    configura el contenedor de dependencias y registra los blueprints.

    Args:
        config: Configuración de la aplicación Flask. Por defecto, se
        utiliza la configuración definida en `settings`.

    Returns:
        Flask: Una instancia de la aplicación Flask configurada.
    """
    # Crea una instancia de Flask
    app = Flask(__name__)

    # Configura la aplicación con el objeto de configuración proporcionado
    app.config.from_object(config)

    # Inicializa la base de datos con la configuración de la aplicación
    db_setup.init_app(app)

    # Configura el manejador de inicio de sesión
    login_manager.init_app(app)

    # Crea e inicializa el contenedor de dependencias
    container = Container()
    container.config.db_schema.from_value(
        app.config.get('DB_SCHEMA', 'public'))  # Configura el esquema de la base de datos

    # Asocia el contenedor a la aplicación para su uso posterior
    app.container = container

    # Registra el inicio de sesión en la aplicación
    register_login(app, container.user_service())

    # Registra todos los blueprints en la aplicación
    register_all_blueprints(
        app,
        container.user_service(),  # Servicio de usuario
        container.dashboard_service(),  # Servicio de dashboard
        None,  # Parámetro opcional (sin uso en este caso)
        container.active_staff_service()  # Servicio de personal activo
    )

    # Devuelve la instancia de la aplicación Flask configurada
    return app