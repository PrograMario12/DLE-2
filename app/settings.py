''' This module contains the settings of the application. '''

import flask
from flask import (
    request,
    render_template,
    redirect
)
from flask_login import (
    login_required,
    UserMixin,
    login_user,
    logout_user
)

from app import app, functions, login_manager

class User(UserMixin):
    ''' This class represents a user. '''
    def __init__(self, user_id):
        self.user_id = user_id

    def get_user_id(self):
        ''' This function returns the user id. '''
        return str(self.user_id)

# Simulate a user database
users = {1: User(1)}

@login_manager.user_loader
def load_user(user_id):
    ''' This function loads a user. '''
    return users.get(int(user_id))


@app.route('/settings')
@login_required
def settings():
    ''' This function renders the settings page. '''
    lines = functions.get_lines()
    lines_capacity = [line[1] for line in lines]

    context = {
        'css_file': 'static/css/styles.css',
        'number_of_buttons': len(lines_capacity),
        'lines': lines_capacity,
        'active_line': request.cookies.get('line')
    }

    return render_template('ajustes.html', **context)

@app.route('/changeLine')
@login_required
def changeLine():
    line = request.args.get('line')
    logout_user()
    # Create a cookie named 'line' with the value of the selected 
    # line
    response = flask.make_response(redirect('/'))
    response.set_cookie('linea', line)
    return response

@app.errorhandler(401)
def unauthorized(e):

    context = {
        'css_file': 'static/css/styles.css',
    }

    return render_template('unauthorized.html', **context)

@app.errorhandler(404)
def page_not_found(e):

    context = {
        'css_file': 'static/css/not_found.css',
    }

    return render_template('not_found.html', **context)

@app.route('/login')
def login():

    context = {
        'css_file': 'static/css/styles.css',
    }
    return render_template('login.html', **context)

@app.route('/login_validation', methods=['POST'])
def login_validation():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == 'admin':
        login_user(User(1))
        return redirect('/settings')
    else:
        return redirect('/')

@app.route('/general_exit_from_line')
def general_exit_from_line():
    production_line = request.cookies.get('linea')
    query_general_exit_from_line(production_line)
    logout_user()
    return redirect('/')

@app.route('/change_of_employees_from_line', methods=['POST'])
@login_required
def change_of_employees_from_line():
    production_line = request.form['line']
    # query_general_exit_from_line(production_line)
    logout_user()
    # return redirect('/')

    return ('La línea de producción ha sido cambiada exitosamente ' 
            + production_line)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')




def query_general_exit_from_line(production_line):
    query = """
    UPDATE registers
        SET exit_hour = NOW()
        WHERE production_line = '{}'
        AND exit_hour IS NULL
    """.format(production_line)

    functions.insert_bd(query)

def query_change_of_employees_from_line(production_line):
    query = """
    UPDATE registers
        SET exit_hour = NOW()
        WHERE production_line = '{}'
        AND exit_hour IS NULL
    """.format(production_line)

    functions.insert_bd(query)
