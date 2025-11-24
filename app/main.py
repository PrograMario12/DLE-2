"""
app/main.py
Fábrica de la aplicación Flask.
"""

from flask import Flask  # Se importa Flask porque es el framework base para crear la aplicación web.
from .config.settings import settings  # Se importa la configuración para centralizar parámetros y facilitar cambios.
from .containers import Container  # Se importa el contenedor de dependencias para gestionar instancias y servicios.
from .extensions import login_manager  # Se importa el manejador de login para controlar la autenticación de usuarios.
from .api.v1.blueprints import register_all_blueprints  # Se importa la función para registrar rutas y modularizar la app.
from .infra.db import db as db_setup  # Se importa la inicialización de la base de datos para conectar la app con el almacenamiento.
from .infra.http.auth import register_login  # Se importa la función para registrar el login y asegurar el acceso.

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
    # Se crea la instancia principal de Flask para iniciar la aplicación.
    app = Flask(__name__)

    # Se carga la configuración para adaptar la app a distintos entornos y necesidades.
    app.config.from_object(config)

    # Se inicializa la base de datos para que la app pueda interactuar con los datos persistentes.
    db_setup.init_app(app)

    # Se inicializa el manejador de login para habilitar la autenticación de usuarios.
    login_manager.init_app(app)

    # Se crea el contenedor de dependencias para desacoplar la lógica y facilitar pruebas/mantenimiento.
    container = Container()
    container.config.db_schema.from_value(
        app.config.get('DB_SCHEMA', 'public'))  # Se configura el esquema de la base de datos para adaptarse a diferentes entornos.

    # Se asocia el contenedor a la app para que los servicios estén disponibles globalmente.
    app.container = container

    # Se registra el login usando el servicio de usuario para controlar el acceso.
    register_login(app, container.user_service())

    # Se registran todos los blueprints para organizar las rutas y funcionalidades de la app.
    register_all_blueprints(
        app,
        container.user_service(),  # Se pasa el servicio de usuario para las rutas que lo requieran.
        container.dashboard_service(),  # Se pasa el servicio de dashboard para las rutas relacionadas.
        container.station_service(),  # Se pasa el servicio de estación aunque no se use, por compatibilidad.
        container.active_staff_service(),  # Se pasa el servicio de personal activo para las rutas correspondientes.
        container.production_lines_service() # Se pasa el servicio de líneas de producción para las rutas que lo necesiten.
    )

    # Se retorna la instancia de la aplicación ya configurada para que pueda ejecutarse.
    return app
