from flask import Blueprint, render_template, request, make_response, redirect, \
    url_for
from app.domain.services.user_service import UserService

# Se crea el Blueprint para las rutas de configuración
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

# Placeholder para el servicio que será inyectado
user_service: UserService


@settings_bp.route('/', methods=['GET', 'POST'])
def configure_line_and_station():
    """
    Gestiona la selección de línea y estación por parte del usuario.
    En GET, muestra las opciones.
    En POST, guarda las selecciones en cookies y redirige.
    """
    if request.method == 'POST':
        # 1. Extraer los datos del formulario enviado por el usuario
        selected_line = request.form.get('line')

        # 2. Crear una respuesta de redirección a la página principal
        # Esto indica que la configuración fue exitosa
        response = make_response(redirect(url_for('main.home')))

        # 3. Guardar la línea seleccionada en una cookie
        if selected_line:
            response.set_cookie('line', selected_line)

        return response

    # Para el método GET:
    # 1. Llamar al servicio para obtener la lista de líneas disponibles
    available_lines = user_service.get_all_lines_for_settings()

    # 2. Renderizar la plantilla de ajustes, pasándole los datos
    return render_template('ajustes.html', lines=available_lines)