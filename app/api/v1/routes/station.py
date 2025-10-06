from flask import Blueprint, render_template, request, current_app
from app.domain.services.station_service import StationService

# La inyección del servicio se hará al registrar el blueprint
station_bp = Blueprint('station', __name__)
service: StationService

@station_bp.route('/successful')
def successful():
    """Muestra la pantalla de éxito tras un registro."""
    card_number = int(request.cookies.get('employee_number', 0))

    display_data = service.get_user_status_for_display(card_number)

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
