from flask import Blueprint, render_template, request, current_app
from app.domain.services.station_service import StationService

# La inyección del servicio se hará al registrar el blueprint
station_bp = Blueprint('station', __name__)
service: StationService  # Placeholder para el servicio inyectado

@station_bp.route('/')
def home():
    """Renderiza la página de inicio."""
    # Lógica de cookies y contexto se mantiene aquí por ser de presentación
    context = {'css_file': 'static/css/init_styles.css'}
    return render_template('index.html', **context)

@station_bp.route('/successful')
def successful():
    """Muestra la pantalla de éxito tras un registro."""
    card_number = int(request.cookies.get('employee_number', 0))

    # La ruta solo orquesta: pide datos al servicio y los pasa a la vista
    display_data = service.get_user_status_for_display(card_number)

    # El servicio devuelve un diccionario listo para el contexto
    context = {
        'css_file': 'static/css/styles.css',
        'user': display_data.get("user"),
        'line': display_data.get("line_name"),
        'station': display_data.get("station_name"),
        'tipo': display_data.get("type"),
        'image': f'static/img/media/{display_data.get("image")}',
        'color_class': display_data.get("color")
    }
    return render_template('successful.html', **context)