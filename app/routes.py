from app import app, functions
from flask import redirect
from app import app
from flask import redirect, render_template

@app.route("/")
def home():
    return render_template('index.html', css_file='static/css/stylesinicio.css')


@app.route('/menuLinea')
def menuLinea():
    resultados = functions.obtener_lineas()
    numero_lineas = len(resultados)
    empleados_por_linea = functions.obtener_empleados_por_linea()
    empleados_por_linea = {int(linea[0]): linea[1] for linea in empleados_por_linea}
    no_hay_lineas = []

    lineas = []
    for resultado in resultados:
        linea = [resultado[0], resultado[2]]
        if resultado[0] in empleados_por_linea:
            linea.append(empleados_por_linea[resultado[0]])
        else:
            linea.append(0)
        lineas.append(linea)

    context = {
        'css_file': 'static/css/styles.css',
        'tipo_seleccion': 'línea',
        'num_cards': numero_lineas,
        'lineas_capacidad_operadores': lineas,
        'lineas': no_hay_lineas
    }

    return render_template('menu.html', **context)


# @app.route('/index')
# def index():
#     return "Hello, World!"
