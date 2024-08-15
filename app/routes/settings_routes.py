from flask import Blueprint, render_template
import functions

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/ajustes')
def ajustes():
    lineas = functions.obtener_lineas()
    lineas_capacidad = [linea[1] for linea in lineas]

    context = {
        'css_file': 'static/css/styles.css',
        'num_botones': len(lineas_capacidad),
        'lineas': lineas_capacidad
    }

    return render_template('ajustes.html', **context)