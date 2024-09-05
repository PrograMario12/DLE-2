from app import app, functions, login_manager
from flask import redirect, render_template, request
from flask_login import login_required, UserMixin, login_user, logout_user
import flask

class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return str(self.id)

#Simular una base de datos de usuarios
users = {1: User(1)}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))


@app.route('/settings')
@login_required
def settings():
    lineas = functions.get_lines()
    lineas_capacidad = [linea[1] for linea in lineas]

    context = {
        'css_file': 'static/css/styles.css',
        'num_botones': len(lineas_capacidad),
        'lineas': lineas_capacidad,
        'active_line': request.cookies.get('linea')
    }

    return render_template('ajustes.html', **context)

@app.route('/changeLine')
@login_required
def changeLine():
    line = request.args.get('line')
    logout_user()
    # Create a cookie named 'linea' with the value of the selected line
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

@app.route('/change_of_employees_from_line')

def query_general_exit_from_line(production_line):
    query = """
    UPDATE registers
        SET exit_hour = NOW()
        WHERE production_line = '{}'
        AND exit_hour IS NULL
    """.format(production_line)

    functions.insert_bd(query)