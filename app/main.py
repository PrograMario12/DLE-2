from flask import Flask
from .config.settings import settings
from .extensions import \
    login_manager  # Ya no necesitamos importar 'db' de aquí
from .api.v1.blueprints import register_all_blueprints
from .domain.services.user_service import UserService
from .domain.services.dashboard_service import DashboardService
from .infra.db.user_repository_sql import UserRepositorySQL
from .infra.db import db as db_setup  # Importamos nuestro nuevo módulo


def create_app(config=settings):
    """Fábrica de la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(config)

    db_setup.init_app(app)
    login_manager.init_app(app)

    schema = app.config.get('DB_SCHEMA', 'public')
    # Inyectamos el esquema al crear el repositorio
    user_repo = UserRepositorySQL(schema=schema)

    user_service = UserService(user_repo)
    dashboard_service = DashboardService(user_repo)

    @login_manager.user_loader
    def load_user(user_id: str):
        with app.app_context():
            # Usamos la misma instancia de user_repo que ya creamos
            return user_repo.find_by_id(int(user_id))

    register_all_blueprints(app, user_service, dashboard_service)

    return app