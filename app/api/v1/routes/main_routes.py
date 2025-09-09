"""
    app/api/v1/routes/main_routes.py
    Rutas principales de la aplicación.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    make_response,
    redirect,
    url_for
)

from app.domain.services.user_service import UserService
from app.domain.services.dashboard_service import DashboardService

# Se crea el Blueprint para las rutas principales
main_bp = Blueprint('main', __name__)

# Placeholders para los servicios que serán inyectados
user_service: UserService
dashboard_service: DashboardService

@main_bp.route('/')
def home():
    """
    Renderiza la página principal de la aplicación.

    Funcionalidad:
        - Establece una cookie con el número de empleado inicializado en '0'.
        - Renderiza la plantilla 'index.html' con un archivo CSS inicial.

    Returns:
        - Una respuesta HTTP con la plantilla renderizada y la cookie configurada.
    """
    context = {'css_file': 'static/css/init_styles.css'}
    response = make_response(render_template('index.html', **context))
    response.set_cookie('employee_number', '0')
    return response


@main_bp.route('/successful')
def successful():
    """
    Renderiza la página de éxito con información del usuario.

    Funcionalidad:
        - Obtiene el número de empleado de las cookies.
        - Recupera la información del usuario para mostrar.
        - Renderiza la plantilla 'successful.html' con los datos del usuario.

    Returns:
        - Una respuesta HTTP con la plantilla renderizada.
    """
    employee_number = int(request.cookies.get('employee_number', 0))

    user_info = main_bp.user_service.get_user_info_for_display(employee_number)

    context = {
        'css_file': 'static/css/styles.css',
        'user': user_info['name'],
        'image': f"static/img/media/{user_info['id']}.png"
    }
    return render_template('successful.html', **context)


@main_bp.route('/menuStation', methods=['GET', 'POST'])
def menu_station():
    """
    Muestra el menú de estaciones para la línea seleccionada.

    Funcionalidad:
        - Verifica si la cookie de línea está configurada, de lo contrario redirige a la configuración.
        - Obtiene el número de empleado del formulario enviado.
        - Determina el último tipo de registro del usuario.
        - Si el último registro es de tipo 'Exit', redirige a la página de éxito.
        - Prepara los datos del tablero de la estación y renderiza la plantilla 'menu.html'.

    Returns:
        - Una redirección a otra ruta si faltan datos o el último registro es 'Exit'.
        - Una respuesta HTTP con la plantilla renderizada y la cookie actualizada.
    """
    line_cookie = request.cookies.get('line')
    print("La línea es:", line_cookie)
    if not line_cookie:
        return redirect(url_for('settings.configure_line_and_station'))

    employee_number = request.form.get('employee_number')
    if not employee_number:
        return redirect(url_for('main.home'))

    last_register_type = main_bp.user_service.get_user_last_register_type(
        employee_number)

    if last_register_type == 'Exit':
        response = make_response(redirect(url_for('main.successful')))
        response.set_cookie('employee_number', employee_number)
        return response

    dashboard_data = main_bp.dashboard_service.get_station_details_for_line(
        int(line_cookie))

    response = make_response(
        render_template('menu.html', **dashboard_data)
    )
    response.set_cookie('employee_number', str(employee_number))
    return response
