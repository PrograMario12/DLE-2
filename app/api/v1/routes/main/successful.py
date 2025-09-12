"""GET /successful — Vista de éxito con datos del usuario."""
from flask import Blueprint, render_template, request, url_for, redirect
from app.domain.services.user_service import UserService
from app.api.v1.schemas.main import EmployeeCookie

def register_successful(bp: Blueprint, user_service: UserService) -> None:
    """
    Registra la ruta para la vista de éxito en el blueprint proporcionado.

    Args:
        bp (Blueprint): El blueprint en el que se registrará la ruta.
        user_service (UserService): Servicio para manejar la lógica de negocio relacionada con usuarios.
    """
    @bp.get("/successful", endpoint="successful")
    def successful():
        """
        Maneja la solicitud GET para la vista de éxito.

        Funcionalidad:
            - Valida la cookie 'employee_number' utilizando el esquema EmployeeCookie.
            - Si la validación falla, redirige a la página de inicio.
            - Obtiene información del usuario a través del servicio de usuario.
            - Renderiza la plantilla 'successful.html' con el contexto del usuario.

        Returns:
            Response: La respuesta HTTP con la plantilla renderizada o una redirección.
        """
        try:
            # Valida la cookie 'employee_number' utilizando el esquema EmployeeCookie
            data = EmployeeCookie.model_validate(
                {"employee_number": request.cookies.get("employee_number", "0")}
            )
        except Exception:
            # Redirige a la página de inicio si la validación falla
            return redirect(url_for("main.home"))

        # Obtiene información del usuario para mostrar
        info = user_service.get_user_info_for_display(data.employee_number)

        # Contexto para renderizar la plantilla
        ctx = {
            "css_href": url_for("static", filename="css/styles.css"),  # URL del archivo CSS
            "user": info["name"],  # Nombre del usuario
            "image": url_for("static", filename=f"img/media/{info['id']}.png"),  # URL de la imagen del usuario
        }

        # Renderiza la plantilla con el contexto
        return render_template("successful.html", **ctx)