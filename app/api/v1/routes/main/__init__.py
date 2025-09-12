"""Fábrica del blueprint principal (Main)."""
from flask import Blueprint
from app.domain.services.user_service import UserService
from app.domain.services.dashboard_service import DashboardService
from .home import register_home
from .successful import register_successful
from .menu_station import register_menu_station

def create_main_bp(user_service: UserService,
                   dashboard_service: DashboardService) -> Blueprint:
    """
    Crea y configura el blueprint principal de la aplicación.

    Args:
        user_service (UserService): Servicio para manejar la lógica de negocio relacionada con usuarios.
        dashboard_service (DashboardService): Servicio para manejar la lógica de negocio relacionada con tableros.

    Returns:
        Blueprint: El blueprint principal configurado con sus rutas registradas.
    """
    bp = Blueprint("main", __name__)  # Crea el blueprint principal con el nombre 'main'
    register_home(bp)  # Registra las rutas relacionadas con la página de inicio
    register_successful(bp, user_service)  # Registra las rutas relacionadas con operaciones exitosas
    register_menu_station(bp, user_service, dashboard_service)  # Registra las rutas relacionadas con el menú de estaciones
    return bp