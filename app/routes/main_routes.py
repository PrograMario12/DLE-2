from flask import Blueprint, render_templatem, request 
from datetime import datetime
import functions

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/exito')
def exito():
    estacion = request
    hora = datetime.now()
    user.set_hora(hora)

    numeroempleado = request.cookies.get('numeroempleado')

    usuario = functions.obtener_usuario(numeroempleado)
    imagen = functions.obtener_imagen(numeroempleado)
    imagen = 'static/img/media/' + str(imagen) + '.png'

    if not usuario:
        usuario = 'Error'

    tipo = functions.get_last_register_type(numeroempleado)

    if tipo == 'Entry':
        functions.register_entry(numeroempleado, request.cookies.get('linea'), estacion, hora)
        linea = request.cookies.get('linea')
        tipo = 'Entrada'
    else:
        functions.register_exit(numeroempleado, hora)
        tipo = 'Salida'
        linea, estacion = functions.get_values_for_exit(numeroempleado)

    context = {
        'css_file': 'static/css/styles.css',
        'usuario': usuario,
        'horario': hora,
        'linea': linea,
        'estacion': estacion,
        'tipo': tipo,
        'imagen': imagen
    }
    return render_template('exito.html', **context)

