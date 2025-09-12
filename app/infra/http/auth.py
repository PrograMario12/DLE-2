# app/infra/http/auth.py

from flask import Flask
from app.extensions import login_manager
from app.domain.services.user_service import UserService

def register_login(app: Flask, user_service: UserService) -> None:
    """
    Registra el manejador de inicio de sesión en la aplicación Flask.

    Args:
        app (Flask): La instancia de la aplicación Flask.
        user_service (UserService): Servicio para manejar la lógica de
        negocio relacionada con usuarios.
    """
    login_manager.init_app(app)  # Inicializa el manejador de inicio de
    # sesión con la aplicación

    @login_manager.user_loader
    def _load(uid: str):
        """
        Carga un usuario desde el servicio de usuarios dado su ID.

        Args:
            uid (str): El ID del usuario a cargar.

        Returns:
            User: Una instancia del usuario si se encuentra, o None si no.
        """
        try:
            return user_service.get_by_id(int(uid))  # Intenta obtener
            # el usuario por su ID
        except ValueError:
            return None  # Devuelve None si el ID no es válido