"""
Registro de rutas para el menú de estación.
Mantiene endpoints: /menuStation (GET/POST) y /afeMenu (GET).
"""
from __future__ import annotations
from flask import Blueprint
from app.domain.services.user_service import UserService
from app.domain.services.dashboard_service import DashboardService
from .controllers import menu_station_post, afe_menu_get

def register_menu_station(bp: Blueprint,
                          user_service: UserService,
                          dashboard_service: DashboardService) -> None:
    """Inyecta servicios y registra endpoints en el Blueprint."""

    # Cierre (closure) con DI simple; evita globals
    def _menu_station():
        return menu_station_post(user_service=user_service,
                                 dashboard_service=dashboard_service)

    def _afe_menu():
        return afe_menu_get()

    bp.add_url_rule("/menuStation", view_func=_menu_station,
                    methods=["GET", "POST"], endpoint="menu_station")

    bp.add_url_rule("/afeMenu", view_func=_afe_menu,
                    methods=["GET"], endpoint="afe_menu")
