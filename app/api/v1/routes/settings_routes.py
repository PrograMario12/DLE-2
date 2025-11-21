"""
    src/api/v1/routes/settings_routes.py
    Rutas para la configuración de línea y estación.
"""

from flask import Blueprint, render_template, request, make_response, redirect, \
    url_for  # Se importan utilidades de Flask para estructurar rutas, manejar peticiones y respuestas, y facilitar la navegación.

from app.domain.services.user_service import \
    UserService  # Se importa el servicio de usuario para delegar la lógica de negocio y mantener el código desacoplado.

settings_bp = Blueprint('settings', __name__,
                        url_prefix='/settings')  # Se crea un Blueprint para modularizar las rutas y facilitar su mantenimiento.

user_service: UserService  # Se declara el servicio como placeholder para inyectarlo después y así poder usarlo en las rutas.


@settings_bp.route('/', methods=['GET',
                                 'POST'])  # Se define la ruta principal para configuración, permitiendo tanto consultas como envíos de datos.
def configure_line_and_station():
    """
    Gestiona la selección de línea y estación por parte del usuario.

    Métodos:
        - GET: Muestra las opciones de líneas disponibles.
        - POST: Guarda la línea seleccionada en una cookie y
        redirige a la página principal.

    Returns:
        - En GET: Renderiza la plantilla 'ajustes.html' con las
        líneas disponibles.
        - En POST: Redirige a la página principal con la línea
        seleccionada almacenada en una cookie.
    """
    if request.method == 'POST':  # Se verifica si la petición es POST para saber si el usuario envió datos.
        selected_line = request.form.get(
            'line')  # Se obtiene la línea seleccionada del formulario para procesar la preferencia del usuario.

        response = make_response(redirect(url_for(
            'main.home')))  # Se prepara una respuesta que redirige al usuario, indicando que la acción fue exitosa.

        if selected_line:  # Se comprueba que el usuario haya seleccionado una línea para evitar guardar valores nulos.
            response.set_cookie('line',
                                selected_line)  # Se almacena la selección en una cookie para recordar la preferencia en futuras visitas.

        return response  # Se retorna la respuesta para finalizar el flujo POST y redirigir al usuario.

    # Si la petición es GET, se ejecuta el siguiente bloque:
    available_lines = settings_bp.user_service.get_all_lines_for_settings()  # Se consulta al servicio las líneas disponibles para mostrar opciones actualizadas.

    print("Las líneas disponibles son:", available_lines, "\n\n")

    return render_template('ajustes.html',
                           lines=available_lines)  # Se renderiza la plantilla pasando las líneas para que el usuario pueda elegir.
