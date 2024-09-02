from flask import Blueprint, redirect, render_template, request
from datetime import datetime
import flask
from app import functions

main_bp = Blueprint('main', __name__)

user = functions.User(0, 0, 0);



@main_bp.route('/')
def home():
    # Renders the home page.

    user.set_line(request.cookies.get('linea'))

    context = {
        'css_file': 'static/css/init_styles.css',
        'js_file': 'static/js/clock.js',
        'img_file': 'static/img/magna-logo.png'
    }

    response = flask.make_response(render_template('index.html', **context))
    response.set_cookie('employee_number', '0')

    return response



@main_bp.route('/menuStation')
def menuStation():
    # Renders the menu page for the stations.

    if 'linea' not in request.cookies:
        return redirect('/ajustes')

    employee_number = request.args.get('employee_number')
    print('El número de empleado es: ', employee_number)

    type_of_register = functions.get_last_register_type(employee_number)
    print('El tipo de registro es: ', type_of_register)
    if type_of_register == 'Exit':
        response = flask.make_response(redirect('/successful'))
        response.set_cookie('employee_number', employee_number)
        return response

    linea = request.cookies.get('linea')
    lineaname = functions.get_line_id(linea)

    resultados = functions.get_stations(lineaname)
    print('Los resultados son: ', resultados)
    numero_estaciones = len(resultados)
    print('El número de estaciones es: ', numero_estaciones)

    empleados_por_estacion = functions.get_employees_for_station(linea)
    empleados_por_estacion = {estacion[0]: estacion[1] for estacion in empleados_por_estacion}
    estacionesList = sorted(list(set([resultado[0] for resultado in resultados])))

    estaciones = []
    for resultado in resultados:
        estacion = resultado[0]
        capacidadLH = resultado[1]
        operadoresLH = empleados_por_estacion.get(str(estacion) + " LH", 0)
        capacidadRH = resultado[2]
        operadoresRH = empleados_por_estacion.get(str(estacion) + " RH", 0)

        capacidadLH = int(capacidadLH) - int(operadoresLH)
        capacidadRH = int(capacidadRH) - int(operadoresRH)

        estaciones.append([estacion, capacidadLH, operadoresLH, capacidadRH, operadoresRH])

    employees_for_line = functions.get_employees_for_line(linea)
    employees_for_line = int(employees_for_line[0][1]) if employees_for_line else 0

    employees_necessary = int(functions.get_employees_necesary_for_line(linea)[0][0])

    context = {
        'css_file': 'static/css/styles.css',
        'tipo_seleccion': 'estación',
        'num_cards': numero_estaciones,
        'lineas_capacidad_operadores': estaciones,
        'lineas': estacionesList,
        'lineaseleccionada': linea,
        'employees_for_line': employees_for_line,
        'employees_necessary': employees_necessary
    }

    response = flask.make_response(render_template('menu.html', **context))
    response.set_cookie('employee_number', str(employee_number))

    return response



@main_bp.route('/successful')
def successful():
    'Screen when the user has successfully registered an entry or exit'
    estacion = request.args.get('estacion')
    hour = datetime.now()
    user.set_hour(hour)

    usuario = functions.obtener_usuario(request.cookies.get('employee_number'))
    imagen = functions.obtener_imagen(request.cookies.get('employee_number'))
    imagen = 'static/img/media/' + str(imagen) + '.png'

    if not usuario:
        usuario = 'Error'

    tipo = functions.get_last_register_type(request.cookies.get('employee_number'))
    print('El tipo de registro es: ', tipo)

    if tipo == 'Entry':
        functions.register_entry(request.cookies.get('employee_number'), request.cookies.get('linea'), estacion, hour)
        linea = request.cookies.get('linea')
        tipo = 'Entrada'
    else:
        functions.register_exit(request.cookies.get('employee_number'), hour)
        tipo = 'Salida'
        linea = functions.get_values_for_exit(request.cookies.get('employee_number'))[0]
        estacion = functions.get_values_for_exit(request.cookies.get('employee_number'))[1]

    context = {
        'css_file': 'static/css/styles.css',
        'usuario': usuario,
        'horario': hour,
        'linea': linea,
        'estacion': estacion,
        'tipo': tipo,
        'imagen': imagen
    }
    return render_template('successful.html', **context)