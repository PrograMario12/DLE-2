# app/containers.py

from dependency_injector import containers, providers
from .infra.db.user_repository_sql import UserRepositorySQL
from .infra.db.mock_staff_active_repository import (
    MockActiveStaffRepository
)
from .domain.services.user_service import UserService
from .domain.services.dashboard_service import DashboardService
from .domain.services.active_staff_service import ActiveStaffService

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

    # Singleton provider for the UserRepositorySQL, initialized with the
    # database schema
    user_repo = providers.Singleton(
        UserRepositorySQL,
        schema=config.db_schema
    )

    # Singleton provider for the MockActiveStaffRepository
    active_staff_repo = providers.Singleton(MockActiveStaffRepository)

    # Singleton provider for the UserService, which depends on the user
    # repository
    user_service = providers.Singleton(UserService, user_repo)

    # Singleton provider for the DashboardService, which depends on the
    # user repository
    dashboard_service = providers.Singleton(DashboardService, user_repo)

    # Singleton provider for the ActiveStaffService, which depends on
    # the active staff repository
    active_staff_service = providers.Singleton(
        ActiveStaffService,
        active_staff_repo
    )