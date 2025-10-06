"""Fábrica del blueprint principal (Main)."""
from flask import Blueprint
from app.domain.services.user_service import UserService
from app.domain.services.dashboard_service import DashboardService
from app.domain.services.station_service import StationService
from .home import register_home
from .successful import register_successful
from .menu_station import register_menu_station

def create_main_bp(user_service: UserService,
   dashboard_service: DashboardService,
   station_service: StationService) -> Blueprint:
    """
    Crea y configura el blueprint principal de la aplicación.

    Args:
        user_service (UserService): Servicio para manejar la lógica de
        negocio relacionada con usuarios.
        dashboard_service (DashboardService): Servicio para manejar la
        lógica de negocio relacionada con tableros.
        station_service (StationService): Servicio para manejar la
        lógica de negocio relacionada con estaciones.

    Returns:
        Blueprint: El blueprint principal configurado con sus rutas
        registradas.
    """

    bp = Blueprint("main", __name__)

    register_home(bp, user_service)
    register_menu_station(bp, user_service, dashboard_service)
    register_successful(bp, user_service, station_service)
    return bp
