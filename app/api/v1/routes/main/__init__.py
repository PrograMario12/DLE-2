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
        user_service (UserService): Servicio para manejar la lógica de
        negocio relacionada con usuarios.
        dashboard_service (DashboardService): Servicio para manejar la
        lógica de negocio relacionada con tableros.

    Returns:
        Blueprint: El blueprint principal configurado con sus rutas
        registradas.
    """
    bp = Blueprint("main", __name__) #Este es el nombre del blueprint
    register_home(bp, user_service)
    register_successful(bp, user_service)
    register_menu_station(bp, user_service, dashboard_service)
    return bp
