from flask import Blueprint, render_template, request, make_response
from app.domain.services.user_service import UserService

main_bp = Blueprint('main', __name__)

# La inyección se hace en un paso posterior al registrar el blueprint
user_service: UserService


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