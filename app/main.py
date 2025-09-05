from flask import Flask
from .config.settings import settings
from .extensions import db, login_manager
from .api.v1.blueprints import register_all_blueprints
from .domain.services.user_service import UserService
from .domain.services.dashboard_service import DashboardService
from .infra.db.user_repository_sql import UserRepositorySQL
from .infra.db.database_manager import DatabaseManager
from typing import Optional

def create_app(config=settings):
    """Fábrica de la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(config)

    db_manager = DatabaseManager(app)
    db.init_app(app, db_manager)
    login_manager.init_app(app)

    user_repo = UserRepositorySQL()
    user_service = UserService(user_repo)
    dashboard_service = DashboardService(user_repo)

    # --- INICIO DE LA SOLUCIÓN ---
    @login_manager.user_loader
    def load_user(user_id: str) -> Optional[UserService]:
        """
        Función requerida por Flask-Login para cargar un usuario desde la sesión.
        Utiliza nuestro repositorio para obtener los datos.
        """
        return user_repo.find_by_id(int(user_id))

    # --- FIN DE LA SOLUCIÓN ---

    register_all_blueprints(app, user_service, dashboard_service)

    return app