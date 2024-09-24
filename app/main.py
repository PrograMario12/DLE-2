''' This module contains the routes for the main blueprint of the 
application. '''

from datetime import datetime
import flask
import flask_login
from flask import Blueprint, redirect, render_template, request
from flask_login import logout_user


from app import functions

main_bp = Blueprint('main', __name__)

user = functions.User(0, 0, 0)

@main_bp.route('/')
def home():
    ''' Renders the home page of the application. '''
    if flask_login.current_user.is_authenticated:
        logout_user()
    actual_line = request.cookies.get('line')
    station = request.cookies.get('station')
    if not station or station == '0':
        station = 'general'

    context = {
        'css_file': 'static/css/init_styles.css',
        'js_file': 'static/js/clock.js',
        'img_file': 'static/img/magna-logo.png',
        'actual_line': actual_line,
        'station': station
    }

    response = flask.make_response(render_template('index.html',
                                                   **context))
    response.set_cookie('employee_number', '0')

    if not station:
        response.set_cookie('station', '0')

    return response



@main_bp.route('/menuStation', methods=['GET', 'POST'])
def menu_station():
    ''' Renders the menu page for the user to select a station. '''
    if 'line' not in  request.cookies:
        return redirect('/settings')

    employee_number = request.form['employee_number']

    if functions.get_last_register_type(employee_number) == 'Exit':
        response = flask.make_response(redirect('/successful'))
        response.set_cookie('employee_number', employee_number)
        return response

    line = request.cookies.get('line')
    line_name = functions.get_line_id(line)
    resultados = functions.get_stations(line_name)

    if request.cookies.get('station') != '0':
        response = flask.make_response(redirect('/successful'))
        response.set_cookie('employee_number', employee_number)
        return response

    context = create_context_for_menu(resultados, line)

    response = flask.make_response(render_template
                                    ('menu.html', **context)
                                )
    response.set_cookie('employee_number', str(employee_number))
    return response

@main_bp.route('/successful')
def successful():
    'Screen when the user has successfully registered an entry or exit'
    station = request.args.get('estacion')
    if not station:
        station = (request.cookies.get('station') or '') + ' BP'
    hour = datetime.now()
    user.set_hour(hour)

    usuario = functions.get_user(request.cookies.get('employee_number'))
    image = functions.get_image(request.cookies.get('employee_number'))
    image = 'static/img/media/' + str(image) + '.png'

    if not usuario:
        usuario = 'Error'

    tipo = functions.get_last_register_type(request
                                            .cookies
                                            .get('employee_number')
                                        )

    if tipo == 'Entry':
        line = request.cookies.get('line')
        production_line = ' '.join(line.split(' ')[1:])
        functions.register_entry(request.cookies.get('employee_number'),
                     production_line,
                     station,
                     hour
                    )
        tipo = 'Entrada'
    else:
        functions.register_exit(request.cookies.get('employee_number'),
                                hour)
        tipo = 'Salida'
        employee_number = request.cookies.get('employee_number')
        line, station = functions.get_values_for_exit(employee_number)
        if line in ['inyección', 'metalizado']:
            line = 'Área de ' + line
        else:
            line = 'Línea ' + line

    context = {
        'css_file': 'static/css/styles.css',
        'user': usuario,
        'horario': hour,
        'line': line,
        'station': station,
        'tipo': tipo,
        'image': image
    }
    return render_template('successful.html', **context)

def create_context_for_menu(results, line):
    ''' Create the context dictionary for the menu template '''
    numero_estaciones = len(results)
    employees_for_station = get_employees_for_station(line)
    estaciones, list_of_stations = process_stations(results,
                                                employees_for_station
                                            )
    employees_for_line, employees_necessary = get_employee_info(line)

    return {
        'css_file': 'static/css/styles.css',
        'type_of_selection': 'estación',
        'num_cards': numero_estaciones,
        'lineas_capacidad_operadores': estaciones,
        'lineas': list_of_stations,
        'selected_line': line,
        'employees_for_line': employees_for_line,
        'employees_necessary': employees_necessary
    }

def get_employees_for_station(line):
    ''' Get the employees for each station in a dictionary '''
    employees_for_station = functions.get_employees_for_station(line)
    if not employees_for_station:
        return {}
    return {station[0]: station[1] for station in employees_for_station}

def process_stations(results, employees_for_station):
    ''' Process the stations '''
    estaciones = []
    estaciones_set = set()

    for resultado in results:
        station, capacity_lh, capacity_rh = (
                                resultado[0], resultado[1], resultado[2]
                            )
        operators_lh = employees_for_station.get(f"{station} LH", 0)
        if operators_lh == 0:
            operators_lh = employees_for_station.get(f"{station} BP", 0)
        operators_rh = employees_for_station.get(f"{station} RH", 0)

        capacity_lh = int(capacity_lh) - int(operators_lh)
        capacity_rh = int(capacity_rh) - int(operators_rh)

        estaciones.append(
                [station, capacity_lh, operators_lh, capacity_rh,
                operators_rh]
            )
        estaciones_set.add(station)

    list_of_stations = sorted(list(estaciones_set))
    return estaciones, list_of_stations

def get_employee_info(line):
    ''' Get the employee information '''
    employees_for_line = functions.get_employees_for_line(line)
    employees_for_line_count = (int(employees_for_line[0][1])
                                if employees_for_line else 0)
    employees_necessary = int(
                functions.get_employees_necessary_for_line(line)[0][0]
            )
    return employees_for_line_count, employees_necessary
