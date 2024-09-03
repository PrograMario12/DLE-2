from app import app, functions
from flask import redirect, render_template, request
from datetime import datetime
import flask

@app.route('/ajustes')
def ajustes():
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
def changeLine():
    line = request.args.get('line')
    # Create a cookie named 'linea' with the value of the selected line
    response = flask.make_response(redirect('/'))
    response.set_cookie('linea', line)
    return response