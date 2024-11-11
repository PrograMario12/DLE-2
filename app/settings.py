''' This module contains the settings of the settings_application. '''

import flask
from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    make_response
)
from flask_login import login_required, logout_user, login_user

from app import functions
from app import database
from . import user_model

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
@login_required
def settings():
    ''' This function renders the settings page. '''
    lines = functions.get_lines()

    active_line = int(request.cookies.get('line', 0))


    context = {
        'css_file': 'static/css/styles.css',
        'lines': lines,
        'active_line': active_line
    }

    return render_template('ajustes.html', **context)

@settings_bp.route('/changeLine')
@login_required
def change_line():
    ''' This function changes the production line. '''
    line = int(request.args.get('line'))
    valid_lines = [6, 7]

    if line in valid_lines:
        positions = get_status_positions(line)

        if line == 6:
            title = 'inyectoras'
            prefix = 'INY-'
        else:
            title = 'metalizadoras'
            prefix = ''

        context = {
            'css_file': 'static/css/styles.css',
            'positions': positions,
            'line': line,
            'title': title,
            'prefix': prefix
        }

        response = make_response(render_template
                                 ('seleccionar_inyectoras.html',
                                  **context)
                                )
    else:
        context = { }
        logout_user()
        response = flask.make_response(redirect('/'))

    # Set common cookies
    response.set_cookie('line', str(line))
    if not context:
        response.set_cookie('station', '0')

    return response


@settings_bp.route('/save-active-positions', methods=['POST'])
@login_required
def save_active_positions():
    ''' This function saves the active positions. '''
    positions = request.form.getlist('position')
    positions = [int(position) for position in positions]
    line = int(request.cookies.get('line'))

    status_positions = get_status_positions(line)

    active_positions = set(positions)
    all_positions = {position[0] for position in status_positions}

    capacity_positions = get_capacity_positions(active_positions)
    change_capacity (capacity_positions, line)

    positions_to_activate = active_positions.intersection(all_positions)
    if positions_to_activate:
        query_activate = f"""
        UPDATE position_status ps
            SET is_active = TRUE
            WHERE position_id_fk IN ({','.join(map(str, positions_to_activate))});
        """
        functions.insert_bd(query_activate)

    positions_to_deactivate = all_positions - active_positions
    if positions_to_deactivate:
        query_deactivate = f"""
        UPDATE position_status ps
            SET is_active = FALSE
            WHERE position_id_fk IN ({','.join(map(str, positions_to_deactivate))});
        """
        functions.insert_bd(query_deactivate)

    response = flask.make_response(redirect('/'))
    return response

@settings_bp.errorhandler(401)
def unauthorized(e):
    ''' This function handles unauthorized access. '''

    context = {
        'css_file': 'static/css/styles.css',
        'error': e
    }

    return render_template('unauthorized.html', **context)

@settings_bp.errorhandler(404)
def page_not_found(e):
    ''' This function handles page not found errors. '''

    context = {
        'css_file': 'static/css/not_found.css',
        'error': e
    }

    return render_template('not_found.html', **context)

@settings_bp.route('/login')
def login():
    ''' This function renders the login page. '''

    context = {
        'css_file': 'static/css/styles.css',
    }
    return render_template('login.html', **context)

@settings_bp.route('/login_validation', methods=['POST'])
def login_validation():
    ''' This function validates the login credentials. '''
    username = request.form['username']

    user = user_model.User.get(username)

    if user:
        login_user(user)
        return redirect(url_for('settings.settings'))
    return redirect(url_for('settings.login'))


@settings_bp.route('/general_exit_from_line')
def general_exit_from_line():
    ''' This function logs out all employees from the line. '''
    production_line = request.cookies.get('line')
    query_general_exit_from_line(production_line)
    logout_user()
    return redirect('/')

@settings_bp.route('/change_of_employees_from_line', methods=['POST'])
@login_required
def change_of_employees_from_line():
    ''' This function logs out all employees from the line. '''
    production_line = request.form['line']
    # query_general_exit_from_line(production_line)
    logout_user()
    # return redirect('/')

    return ('La línea de producción ha sido cambiada exitosamente '
            + production_line)

@settings_bp.route('/logout')
@login_required
def logout():
    ''' This function logs out the user. '''
    logout_user()
    return redirect('/')

@settings_bp.route('/settings_line')
@login_required
def settings_line():
    ''' This function renders the settings line page. '''
    context = {
        'css_file': 'static/css/styles.css',
    }

    return render_template('settings_configuration_line.html',
                           **context)

@settings_bp.route('/change_line_unique')
@login_required
def change_line_unique():
    ''' This function changes the production line. '''
    line = request.args.get('line')
    response = flask.make_response(redirect('settings_station_unique'))
    response.set_cookie('line', line)
    return response

@settings_bp.route('/settings_station_unique')
@login_required
def settings_station_unique():
    ''' This function changes the production line. '''
    line = request.cookies.get('line')
    line_id = functions.get_line_id(line)

    stations = [station[0] for station in
                functions.get_stations(line_id)]
    number_of_stations = len(stations)

    context = {
        'css_file': 'static/css/styles.css',
        'stations': stations,
        'number_of_stations': number_of_stations,
    }

    return render_template('settings_configuration_station.html',
                           **context)

@settings_bp.route('/change_station_unique')
@login_required
def change_station_unique():
    ''' This function changes the production line. '''
    station = request.args.get('station')
    logout_user()
    response = flask.make_response(redirect('/'))
    response.set_cookie('station', station)
    return response

def query_general_exit_from_line(production_line):
    ''' This function logs out all employees from a line. '''
    query = f"""
    UPDATE registers
        SET exit_hour = NOW()
        WHERE production_line = '{production_line}'
        AND exit_hour IS NULL
    """

    functions.insert_bd(query)

def query_change_of_employees_from_line(production_line):
    ''' This function logs out all employees from a line. '''
    query = f"""
    UPDATE registers
        SET exit_hour = NOW()
        WHERE production_line = '{production_line}'
        AND exit_hour IS NULL
    """

    functions.insert_bd(query)

def get_status_positions(line_id):
    ''' This function gets the status of the positions. '''
    query = f"""
    SELECT p.position_id, p.position_name, ps.is_active
      FROM positions p
      INNER JOIN position_status ps
      ON p.position_id = ps.position_id_fk
      WHERE p.line_id = {line_id}
      AND p.position_name NOT LIKE '%afe%'
      ORDER BY p.position_name;
    """

    results = functions.execute_query(query)
    return results

def get_capacity_positions(positions):
    ''' This function gets the capacity of the positions. '''
    db = database.Database()
    query = f"""
    SELECT position_id, sum(employee_capacity)
        FROM positions pos
        INNER JOIN tbl_sides_of_positions sides
          ON sides.position_id_fk = pos.position_id
        WHERE position_id IN ({','.join(map(str, positions))})
        GROUP BY position_id
    """
    db.connect()
    results = db.execute_query(query)
    db.disconnect()


    total_capacity = 0
    if results:
        for result in results:
            total_capacity += result[1]
    return total_capacity

def change_capacity(capacity, line):
    ''' This function changes the capacity of the line. '''
    db = database.Database()
    query = f"""
    UPDATE zones
        SET employee_capacity = {capacity}
        WHERE line_id = {line}
    """

    db.connect()
    db.insert_query(query)
    db.disconnect()
