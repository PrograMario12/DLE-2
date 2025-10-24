"""
Registro de rutas para el menú de estación.
Mantiene endpoints: /menuStation (GET/POST) y /afeMenu (GET).
app/api/v1/routes/main/menu_station/__init__.py
"""

from __future__ import annotations
from flask import Blueprint
from app.domain.services.user_service import UserService
from app.domain.services.dashboard_service import DashboardService
from .controllers import menu_station_post, afe_menu_get

def register_menu_station(bp: Blueprint,
                          user_service: UserService,
                          dashboard_service: DashboardService) -> None:
    """
    Registra los endpoints relacionados con el menú de estación en el Blueprint proporcionado.

    Args:
        bp (Blueprint): El Blueprint de Flask donde se registrarán las rutas.
        user_service (UserService): Servicio para manejar la lógica relacionada con usuarios.
        dashboard_service (DashboardService): Servicio para manejar la lógica del dashboard.

    Notas:
        - Registra dos endpoints:
          1. /menuStation: Soporta métodos GET y POST.
          2. /afeMenu: Soporta solo el método GET.
        - Utiliza closures para inyectar dependencias en las vistas.
    """

    # Cierre (closure) con DI simple; evita el uso de variables globales
    def _menu_station():
        """
        Maneja las solicitudes GET y POST al endpoint /menuStation.

        Returns:
            Response: Respuesta generada por la función `menu_station_post`.
        """
        return menu_station_post(user_service=user_service,
                                 dashboard_service=dashboard_service)

    def _afe_menu():
        """
        Maneja las solicitudes GET al endpoint /afeMenu.

        Returns:
            Response: Respuesta generada por la función `afe_menu_get`.
        """
        return afe_menu_get()

    # Registro del endpoint /menuStation
    bp.add_url_rule("/menuStation", view_func=_menu_station,
                    methods=["GET", "POST"], endpoint="menu_station")

    # Registro del endpoint /afeMenu
    bp.add_url_rule("/afeMenu", view_func=_afe_menu,
                    methods=["GET"], endpoint="afe_menu")