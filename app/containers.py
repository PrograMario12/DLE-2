# app/containers.py

from dependency_injector import containers, providers

from .domain.services.production_lines_service import ProductionLinesService
from app.infra.db.active_staff_repository_sql import ActiveStaffRepositorySQL
from .infra.db.production_lines_repository_sql import ProductionLineRepositorySQL
from .infra.db.register_repository_sql import RegisterRepositorySQL
from .infra.db.user_repository_sql import UserRepositorySQL
from .domain.services.user_service import UserService
from .domain.services.dashboard_service import DashboardService
from .domain.services.active_staff_service import ActiveStaffService
from .domain.services.station_service import StationService

class Container(containers.DeclarativeContainer):
    """
    Dependency injection container for managing application services and
    repositories.

    This container uses the `dependency_injector` library to define and
    provide dependencies as singletons. It centralizes the configuration
    and instantiation of repositories and services used throughout the
    application.
    """

    # Configuration provider for external settings (e.g., database schema)
    config = providers.Configuration()

    # Singleton provider for the UserRepositorySQL
    user_repo = providers.Singleton(
        UserRepositorySQL,
        schema=config.db_schema
    )

    # Singleton provider for the ProductionLineRepositorySQL
    production_line_repo = providers.Singleton(
        ProductionLineRepositorySQL, 
        schema=config.db_schema
    )

    # Singleton provider for the RegisterRepositorySQL
    register_repo = providers.Singleton(
        RegisterRepositorySQL,
        schema=config.db_schema
    )

    # Singleton provider for the MockActiveStaffRepository
    active_staff_repo = providers.Singleton(ActiveStaffRepositorySQL, config.db_schema)

    # Singleton provider for the UserService
    user_service = providers.Singleton(
        UserService, 
        user_repo,
        production_line_repo,
        register_repo
    )

    # Singleton provider for the ProductionLinesService
    production_lines_service = providers.Singleton(ProductionLinesService,
                                                   production_line_repo)

    # Singleton provider for the DashboardService
    dashboard_service = providers.Singleton(DashboardService, user_repo, production_line_repo)

    # Singleton provider for the StationService
    station_service = providers.Singleton(StationService, user_repo, register_repo)

    # Singleton provider for the ActiveStaffService
    active_staff_service = providers.Singleton(
        ActiveStaffService,
        active_staff_repo
    )