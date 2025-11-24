"""
Fábrica del blueprint principal (Main).
api/v1/routes/main/__init__.py
"""
from flask import Blueprint

from app.domain.repositories.IProductionLinesRepository import \
    IProductionLinesRepository
from app.domain.services.user_service import UserService
from app.domain.services.dashboard_service import DashboardService
from app.domain.services.station_service import StationService
from app.domain.services.active_staff_service import ActiveStaffService
from .home import register_home
from .successful import register_successful
from .menu_station import register_menu_station
from .employees import register_employees

def create_main_bp(user_service: UserService,
    dashboard_service: DashboardService,
    station_service: StationService,
    active_staff_service: ActiveStaffService,
    production_lines_service: IProductionLinesRepository
    ) -> Blueprint:
    """
    Crea y configura el blueprint principal de la aplicación.

    Args:
        user_service (UserService): Servicio para manejar la lógica de
        negocio relacionada con usuarios.
        dashboard_service (DashboardService): Servicio para manejar la
        lógica de negocio relacionada con tableros.
        station_service (StationService): Servicio para manejar la
        lógica de negocio relacionada con estaciones.
        active_staff_service (ActiveStaffService): Servicio para manejar
        la lógica de negocio relacionada con empleados activos.

    Returns:
        Blueprint: El blueprint principal configurado con sus rutas
        registradas.
    """

    bp = Blueprint("main", __name__)

    register_home(bp, user_service, production_lines_service)
    register_menu_station(bp, user_service, dashboard_service)
    register_successful(bp, user_service, station_service)
    register_employees(bp, active_staff_service)

    return bp
