''' This module contains the routes for the main blueprint of the
application. '''

from datetime import datetime
import flask
import flask_login
from flask import Blueprint, redirect, render_template, request
from flask_login import logout_user
from app import functions
from app.model import dashboard_model
from app import database


main_bp = Blueprint('main', __name__)

user = functions.User(0, 0, 0)

@main_bp.route('/')
def home():
    ''' Renders the home page of the application. '''
    dm = dashboard_model.StationsDashboard()
    if flask_login.current_user.is_authenticated:
        logout_user()
    actual_line = int(request.cookies.get('line'))
    line_name = dm.get_line(actual_line)
    station = request.cookies.get('station')
    station_text = 'general'
    if station and station != '0':
        station_text = station

    context = {
        'css_file': 'static/css/init_styles.css',
        'js_file': 'static/js/clock.js',
        'img_file': 'static/img/magna-logo.png',
        'actual_line': line_name,
        'station': station_text
    }

    response = flask.make_response(render_template('index.html',
                                                   **context))
    response.set_cookie('employee_number', '0')

    if not station:
        print('Station is None')
        response.set_cookie('station', '0')

    return response

@main_bp.route('/menuStation', methods=['GET', 'POST'])
def menu_station():
    ''' Renders the menu page for the user to select a station. '''
    if 'line' not in  request.cookies:
        return redirect('/settings')

    employee_number = request.form['employee_number']
    line = int(request.cookies.get('line'))

    if functions.get_last_register_type(employee_number) == 'Exit':
        response = flask.make_response(redirect('/successful'))
        response.set_cookie('employee_number', employee_number)
        return response

    if request.cookies.get('station') != '0':
        response = flask.make_response(redirect('/successful'))
        response.set_cookie('employee_number', employee_number)
        return response

    dm = dashboard_model.StationsDashboard()
    card_data = dm.create_stations_dashboard(line)
    line_name = dm.get_line(line)

    total_capacity = 0
    total_employees = 0

    for card in card_data:
        for side in card['sides']:
            total_capacity += side['employee_capacity']
            total_employees += side['employees_working']

    total_capacity = total_capacity - 1
    total_employees = max(0, total_employees - total_capacity)

    tipo = 'Estación'

    context = {
        'css_file': 'static/css/styles.css',
        'cards': card_data,
        'line': line_name,
        'total_capacity': total_capacity,
        'total_employees': total_employees,
        'tipo': tipo
    }

    response = flask.make_response(render_template
                                    ('menu.html', **context))
    response.set_cookie('employee_number', str(employee_number))
    return response

@main_bp.route('/successful')
def successful():
    '''Screen when the user has successfully registered an entry or
    exit'''
    station = request.args.get('id')
    dm = dashboard_model.StationsDashboard()
    print('Station:', station)
    employee_number = int(request.cookies.get('employee_number'))
    # if not station:
    #     station = (request.cookies.get('station') or '') + ' BP'
    hour = datetime.now()

    info_user = get_info_user(employee_number)

    image = 'static/img/media/' + str(info_user['id']) + '.png'

    tipo = functions.get_last_register_type(employee_number)

    if tipo == 'Entry':
        line = int(request.cookies.get('line'))
        line_name = dm.get_line(line)
        station_name = get_position_name(int(station))
        functions.register_entry(employee_number,
                     line,
                     station,
                     hour,
                    )
        tipo = 'Entrada'
        color_class = 'employee-ok'
    else:
        color_class = 'employee-warning'
        functions.register_exit(employee_number,
                                hour)
        tipo = 'Salida'

        line_name, station_name = get_values_for_exit(employee_number)

    context = {
        'css_file': 'static/css/styles.css',
        'user': info_user['name'],
        'line': line_name,
        'station': station_name,
        'tipo': tipo,
        'image': image,
        'color_class': color_class
    }
    return render_template('successful.html', **context)

def get_info_user(employee_number):
    ''' Gets the information of the user. '''
    db = database.Database()
    query = f"""
    SELECT id_empleado, nombre_empleado, apellidos_empleado
        FROM table_empleados_tarjeta
        WHERE numero_tarjeta = {employee_number}
        LIMIT 1
    """

    db.connect()
    results = db.execute_query(query)

    if not results:
        return {
            'id': None,
            'name': 'Usuario aún no registrado'
        }
    info = {
        'id': results[0][0],
        'name': f"""{results[0][1]} {results[0][2]}"""
    }

    return info

def get_values_for_exit(user_id):
    ''' Gets the values for exit. '''
    db = database.Database()
    query = f"""
        SELECT z."name" , ps.position_name
            FROM sch_dev.registers r
            INNER JOIN sch_dev.zones z ON z.line_id = r.line_id_fk
            INNER JOIN sch_dev.tbl_sides_of_positions tbl_s ON tbl_s.side_id = r.position_id_fk
            INNER JOIN sch_dev.positions ps ON ps.position_id = tbl_s.position_id_fk 
            WHERE r.id_employee = {user_id}
            ORDER BY r.id_register DESC
            LIMIT 1
        """

    db.connect()
    results = db.execute_query(query)
    db.disconnect()

    if not results:
        return (None, None)
    return (results[0][0], results[0][1])

def get_position_name(position_id):
    ''' Gets the position name. '''
    db = database.Database()
    query = f"""
        SELECT ps.position_name
            FROM sch_dev.tbl_sides_of_positions tbl_ps
            INNER JOIN sch_dev.positions ps ON ps.position_id = tbl_ps.position_id_fk
            WHERE tbl_ps.side_id = {position_id}
        """

    db.connect()
    results = db.execute_query(query)
    db.disconnect()

    if not results:
        return None
    return results[0][0]
