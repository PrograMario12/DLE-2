"""
app/main.py
Fábrica de la aplicación Flask.
Refactorizada para usar Flask-SQLAlchemy, Flask-Migrate y limpiar imports.
"""

from flask import Flask
from .config.settings import settings
from .containers import Container
from .extensions import db, migrate
from .api.v1.blueprints import register_all_blueprints
from .infra.http.auth import register_login
from .infra.db.db import init_app as init_legacy_db

def create_app(config=settings):
    """
    Fábrica de la aplicación Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config)

    # Inicializa SQLAlchemy y Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Inicializa Legacy DB
    init_legacy_db(app)

    # Contenedor de Inyección de Dependencias
    container = Container()
    container.config.db_schema.from_value(
        app.config.get('DB_SCHEMA', 'public')
    )
    app.container = container

    # Auth
    register_login(app, container.user_service())

    # Blueprints
    register_all_blueprints(
        app,
        container.user_service(),
        container.dashboard_service(),
        container.station_service(),
        container.active_staff_service(),
        container.production_lines_service()
    )

    return app
