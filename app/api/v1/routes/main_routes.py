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


main_bp = Blueprint('main', __name__)

# La inyección se hace en un paso posterior al registrar el blueprint
user_service: UserService
dashboard_service: DashboardService

@main_bp.route('/')
def home():
    # La lógica de presentación (cookies, contexto) se queda aquí
    context = {'css_file': 'static/css/init_styles.css'}
    response = make_response(render_template('index.html', **context))
    response.set_cookie('employee_number', '0')
    return response

@main_bp.route('/successful')
def successful():
    employee_number = int(request.cookies.get('employee_number', 0))

    # 1. La ruta llama al servicio para obtener los datos
    user_info = user_service.get_user_info_for_display(employee_number)

    # 2. La ruta prepara el contexto y renderiza
    context = {
        'css_file': 'static/css/styles.css',
        'user': user_info['name'],
        'image': f"static/img/media/{user_info['id']}.png"
        # ... otros datos devueltos por un servicio más completo
    }
    return render_template('successful.html', **context)

@main_bp.route('/menuStation', methods=['GET', 'POST'])
def menu_station():
    """
    Muestra el menú de estaciones para la línea seleccionada en las cookies.
    """
    # 1. Validación de la capa de presentación (API)
    line_cookie = request.cookies.get('line')
    if not line_cookie:
        return redirect(url_for('settings.configure_line_and_station'))

    employee_number = request.form.get('employee_number')
    if not employee_number:
        # Si alguien accede por GET sin venir del formulario, lo redirigimos
        return redirect(url_for('main.home'))

    # 2. Llamada a los servicios para la lógica de negocio
    # Comprobar si el usuario ya debe salir
    last_register_type = user_service.get_user_last_register_type(employee_number)
    if last_register_type == 'Exit':
        response = make_response(redirect(url_for('main.successful')))
        response.set_cookie('employee_number', employee_number)
        return response

    # Obtener los datos del dashboard desde el servicio correspondiente
    dashboard_data = dashboard_service.prepare_station_dashboard(int(line_cookie))

    # 3. Renderizar la plantilla con los datos
    response = make_response(
        render_template('menu.html', **dashboard_data)
    )
    response.set_cookie('employee_number', str(employee_number))
    return response