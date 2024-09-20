''' This module contains the settings of the settings_application. '''

import flask
from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for
)

from flask_login import login_required, logout_user, login_user

from app import functions

from . import user_model

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
@login_required
def settings():
    ''' This function renders the settings page. '''
    lines = functions.get_lines()
    names_lines = [line[1].capitalize() for line
                   in lines]

    context = {
        'css_file': 'static/css/styles.css',
        'number_of_buttons': len(names_lines),
        'lines': names_lines,
        'active_line': request.cookies.get('line')
    }

    return render_template('ajustes.html', **context)

@settings_bp.route('/changeLine')
@login_required
def change_line():
    ''' This function changes the production line. '''
    line = request.args.get('line')
    if line == 'Área inyección':
        line_id = functions.get_line_id(line)
        injectors = get_status_injectors(line_id)
        injectors.pop()

        context = {
            'css_file': 'static/css/styles.css',
            'injectors' : injectors
        }
        return render_template('seleccionar_inyectoras.html', **context)
    logout_user()
    response = flask.make_response(redirect('/'))
    line_id = functions.get_line_id(line)
    response.set_cookie('line', line)
    return response

@settings_bp.route('/save-active-injectors', methods=['POST'])
@login_required
def save_active_injectors():
    ''' This function saves the active injectors. '''
    injectors = request.form.getlist('injectors')

    status_injectors = get_status_injectors(6)

    for injector in status_injectors:
        if injector[0] in injectors:
            query = f"""
            UPDATE position_status ps
                SET is_active = TRUE
                FROM positions p
                WHERE p.position_id = ps.position_id_fk
                AND p.position_name = '{injector[0]}';
            """
        else:
            query = f"""
            UPDATE position_status ps
                SET is_active = FALSE
                FROM positions p
                WHERE p.position_id = ps.position_id_fk
                AND p.position_name = '{injector[0]}'
            """
        functions.insert_bd(query)

    response = flask.make_response(redirect('/'))
    response.set_cookie('line', 'Área inyección')
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

def get_status_injectors(line_id):
    ''' This function gets the status of the injectors. '''
    query = f"""
    SELECT p.position_name, ps.is_active
      FROM positions p
      INNER JOIN position_status ps
      ON p.position_id = ps.position_id_fk
      WHERE p.line_id = {line_id}
      ORDER BY p.position_name;
    """

    results = functions.execute_query(query)
    return results
