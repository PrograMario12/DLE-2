"""
Módulo de rutas para la página de inicio de la aplicación.

Este módulo define y registra la ruta principal ("/") asociada a la página de inicio.
Se encarga de renderizar la plantilla inicial, configurar estilos básicos y establecer
una cookie de control de sesión (`employee_number`).
"""

from flask import (
    Blueprint,
    render_template,
    make_response,
    url_for,
    request
)
from app.domain.services.user_service import UserService

def register_home(bp: Blueprint, user_service: UserService ) -> None:
    """
    Registra la ruta de la página de inicio en el blueprint proporcionado.

    La ruta asociada es `/` con el nombre de endpoint `"home"`.

    Args:
        bp (Blueprint): El blueprint en el que se registrará la ruta.
    """
    @bp.get("/", endpoint="home")
    def home():
        """
        Maneja solicitudes GET para la página de inicio.

        Flujo principal:
            1. Construye la ruta al archivo CSS inicial (`init_styles.css`).
            2. Renderiza la plantilla `index.html`.
            3. Lee la cookie `"line"` (si existe) y la imprime en consola (solo para debug).
            4. Establece la cookie `"employee_number"` con valor `"0"`, accesible
               únicamente por HTTP y con política `SameSite=Lax`.

        Returns:
            flask.Response: Objeto de respuesta HTTP con la plantilla renderizada y
            la cookie configurada.
        """
        line_int = request.cookies.get("line")
        line_name = user_service.get_line_name_by_id(int(line_int)) if (
            line_int) else None
        print(line_name)
        resp = make_response(render_template("index.html", line=line_name))


        resp.set_cookie("employee_number", "0", httponly=True, samesite="Lax")
        return resp
