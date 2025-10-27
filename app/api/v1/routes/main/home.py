"""
Genera las rutas principales de la aplicación.
app/api/v1/routes/main/home.py
"""

from flask import (
    Blueprint,
    render_template,
    make_response,
    request
)
from app.domain.services.user_service import UserService

def register_home(bp: Blueprint, user_service: UserService) -> None:
    """
    Registra la ruta principal (home) en el blueprint proporcionado.

    Args:
        bp (Blueprint): El blueprint en el que se registrará la ruta.
        user_service (UserService): Servicio para manejar la lógica relacionada con usuarios.

    Returns:
        None
    """

    @bp.get("/", endpoint="home")
    def home():
        """
        Controlador para la ruta principal ("/").

        Obtiene el nombre de la línea basado en la cookie "line" y renderiza
        la plantilla "index.html". También establece una cookie "employee_number".

        Returns:
            Response: Respuesta HTTP con la plantilla renderizada.
        """
        # Obtiene el valor de la cookie "line"
        line_int = request.cookies.get("line")

        # Si la cookie "line" existe, obtiene el nombre de la línea usando el servicio de usuario
        line_name = user_service.get_line_name_by_id(int(line_int)) if line_int else None

        # Renderiza la plantilla "index.html" con el nombre de la línea
        resp = make_response(
            render_template(
                "index.html",
                line=line_name
            )
        )

        # Establece una cookie "employee_number" con valor "0"
        resp.set_cookie("employee_number", "0", httponly=True, samesite="Lax")

        return resp