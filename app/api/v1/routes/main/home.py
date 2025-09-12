"""GET / — Home con cookie inicial."""
from flask import Blueprint, render_template, make_response, url_for

def register_home(bp: Blueprint) -> None:
    """
    Registra la ruta para la página de inicio en el blueprint proporcionado.

    Args:
        bp (Blueprint): El blueprint en el que se registrará la ruta.
    """
    @bp.get("/", endpoint="home")
    def home():
        """
        Maneja la solicitud GET para la página de inicio.

        Funcionalidad:
            - Renderiza la plantilla 'index.html' con un enlace al archivo CSS inicial.
            - Establece una cookie 'employee_number' con valor '0', accesible solo por HTTP y con política SameSite=Lax.

        Returns:
            Response: La respuesta HTTP con la plantilla renderizada y la cookie configurada.
        """
        css = url_for("static", filename="css/init_styles.css")  # Genera la URL para el archivo CSS
        resp = make_response(render_template("index.html", css_href=css))  # Renderiza la plantilla y crea la respuesta
        resp.set_cookie("employee_number", "0", httponly=True, samesite="Lax")  # Configura la cookie
        return resp