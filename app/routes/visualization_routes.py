from flask import Blueprint, render_template
import functions

visualization_bp = Blueprint('visualization', __name__)

@visualization_bp.route('/visualizacion')
def visualizaciones():
    resultados = functions.obtener_lineas()
    numero_lineas = len(resultados)
    empleados_por_linea = functions.get_employees_for_line()
    empleados_por_linea = {linea[0]: linea[1] for linea in empleados_por_linea}
    no_hay_lineas = []

    context = {
        'resultados': resultados,
        'numero_lineas': numero_lineas,
        'empleados_por_linea': empleados_por_linea,
        'no_hay_lineas': no_hay_lineas
    }

    return render_template('visualizaciones.html', **context)