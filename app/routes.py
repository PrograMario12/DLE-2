from app import app, functions
from flask import redirect, render_template, request
from datetime import datetime
import flask


user = functions.Usuario(0, 0, 0);


@app.route("/")
def home():
    """
    Renders the home page.

    Returns:
        The rendered template for the home page with the specified CSS and JavaScript files.
    """

    user.set_linea(request.cookies.get('linea'))

    context = {
        'css_file': 'static/css/stylesinicio.css',
        'js_file': 'static/js/reloj.js',
        'img_file': 'static/img/magna-logo.png'
    }

    response = flask.make_response(render_template('index.html', **context))
    response.set_cookie('numeroempleado', '0')

    return response

@app.route('/menuLinea')
def menuLinea():
    numeroempleado = request.args.get('numeroempleado')
    user.set_numero_empleado(numeroempleado)

    tipo = functions.get_last_register_type(user.numero_empleado)
    if tipo == 'Exit':
        return redirect('/exito')

    resultados = functions.get_lines()
    numero_lineas = len(resultados)
    employees_for_line = functions.get_employees_for_line(request.cookies.get('linea'))
    empleados_por_linea = employees_for_line[0][1] if employees_for_line else 0
    empleados_por_linea = {linea[0]: linea[1] for linea in empleados_por_linea}
    no_hay_lineas = []

    lineas = []
    '''
        resultado[0] is equal to the line id
        resultado[2] is equal to the line capacity
    '''
    for resultado in resultados:
        linea = [resultado[1], resultado[2]]
        if resultado[1] in empleados_por_linea:
            linea.append(empleados_por_linea[resultado[1]])
        else:
            linea.append(0)

        #Here we calculate the number of available operators
        linea[1] = int(linea[1]) - int(linea[2])

        #Here we check if the line has available operators
        lineas.append(linea)

    context = {
        'css_file': 'static/css/styles.css',
        'tipo_seleccion': 'línea',
        'num_cards': numero_lineas,
        'lineas_capacidad_operadores': lineas,
        'lineas': no_hay_lineas
    }

    return render_template('menu.html', **context)

@app.route('/menuStation')
def menuStation():
    if 'linea' not in request.cookies:
        return redirect('/ajustes')

    numeroempleado = request.args.get('numeroempleado')
    user.set_numero_empleado(numeroempleado)

    tipo = functions.get_last_register_type(user.numero_empleado)
    if tipo == 'Exit':
        response = flask.make_response(redirect('/exito'))
        response.set_cookie('numeroempleado', numeroempleado)
        return response

    linea = request.cookies.get('linea')
    lineaname = functions.get_line_id(linea)
    user.set_linea(linea)

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
        nombre_operadores_LH = functions.get_names_operators(estacion, linea, 'LH')
        nombre_operadores_RH = functions.get_names_operators(estacion, linea, 'RH')
        
        capacidadLH = int(capacidadLH) - int(operadoresLH)
        capacidadRH = int(capacidadRH) - int(operadoresRH)

        estaciones.append([estacion, capacidadLH, operadoresLH, capacidadRH, operadoresRH, nombre_operadores_LH, nombre_operadores_RH])

    employees_for_line = functions.get_employees_for_line(linea)
    employees_for_line = int(employees_for_line[0][1]) if employees_for_line else 0

    employees_necessary = int(functions.get_employees_necesary_for_line(linea)[0][0])

    print('Las estaciones son:', estaciones)

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
    response.set_cookie('numeroempleado', str(numeroempleado))

    return response


@app.route('/exito')
def exito():
    estacion = request.args.get('estacion')
    hora = datetime.now()
    user.set_hora(hora)

    usuario = functions.obtener_usuario(request.cookies.get('numeroempleado'))
    imagen = functions.obtener_imagen(request.cookies.get('numeroempleado'))
    imagen = 'static/img/media/' + str(imagen) + '.png'

    if not usuario:
        usuario = 'Error'

    tipo = functions.get_last_register_type(request.cookies.get('numeroempleado'))

    if tipo == 'Entry':
        functions.register_entry(request.cookies.get('numeroempleado'), request.cookies.get('linea'), estacion, hora)
        linea = request.cookies.get('linea')
        tipo = 'Entrada'
    else:
        functions.register_exit(request.cookies.get('numeroempleado'), hora)
        tipo = 'Salida'
        linea = functions.get_values_for_exit(request.cookies.get('numeroempleado'))[0]
        estacion = functions.get_values_for_exit(request.cookies.get('numeroempleado'))[1]

    context = {
        'css_file': 'static/css/styles.css',
        'usuario': usuario,
        'horario': hora,
        'linea': linea,
        'estacion': estacion,
        'tipo': tipo,
        'imagen': imagen
    }
    return render_template('exito.html', **context)

@app.route('/ajustes')
def ajustes():
    lineas = functions.get_lines()
    lineas_capacidad = [linea[1] for linea in lineas]

    context = {
        'css_file': 'static/css/styles.css',
        'num_botones': len(lineas_capacidad),
        'lineas': lineas_capacidad
    }

    return render_template('ajustes.html', **context)

@app.route('/visualizaciones')
def visualizaciones():

    resultados = functions.get_lines()
    numero_lineas = len(resultados)
    empleados_por_linea = functions.get_employees_for_line()
    empleados_por_linea = {linea[0]: linea[1] for linea in empleados_por_linea}
    no_hay_lineas = []

    lineas = []
    '''
        resultado[0] is equal to the line id
        resultado[2] is equal to the line capacity
    '''
    for resultado in resultados:
        linea = [resultado[1], resultado[2]]
        if resultado[1] in empleados_por_linea:
            linea.append(empleados_por_linea[resultado[1]])
        else:
            linea.append(0)

        #Here we calculate the number of available operators
        # linea[1] = int(linea[1]) - int(linea[2])

        #Here we check if the line has available operators
        lineas.append(linea)

    context = {
        'css_file': 'static/css/styles.css',
        'tipo_seleccion': 'línea',
        'num_cards': numero_lineas,
        'lineas_capacidad_operadores': lineas,
        'lineas': no_hay_lineas
    }

    return render_template('visualizaciones.html', **context)

@app.route('/visualizacionesEstacion')
def visualizacionesEstacion():
    linea = request.args.get('linea')
    lineaname = functions.get_line_id(linea)

    resultados = functions.get_stations(lineaname)
    # print('Los resultados son: ', resultados)
    numero_estaciones = len(resultados)
    # print('El número de estaciones es: ', numero_estaciones)

    empleados_por_estacion = functions.get_employees_for_station(linea)
    empleados_por_estacion = {estacion[0]: estacion[1] for estacion in empleados_por_estacion}
    estacionesList = sorted(list(set([resultado[0] for resultado in resultados])))

    estaciones = []
    for resultado in resultados:
        estacion = resultado[0]
        print ('La estación es: ', estacion)
        capacidadLH = resultado[1]
        operadoresLH = empleados_por_estacion.get(str(estacion) + " LH", 0)
        capacidadRH = resultado[2]
        operadoresRH = empleados_por_estacion.get(str(estacion) + " RH", 0)
        
        nombre_operadores_LH = functions.get_names_operators(estacion, linea, 'LH')
        # nombre_operadores_LH = ', '.join([f"{nombre[2]} {nombre[0]} {nombre[1]}" for nombre in nombre_operadores_LH]) if nombre_operadores_LH else 'Información no disponible'

        nombre_operadores_RH = functions.get_names_operators(estacion, linea, 'RH')
        # nombre_operadores_RH = ', '.join([f"{nombre[2]} {nombre[0]} {nombre[1]}" for nombre in nombre_operadores_RH]) if nombre_operadores_RH else 'Información no disponible'



        print ('Los operadores son: ', nombre_operadores_LH, nombre_operadores_RH, 'en la estación', estacion)
        
        capacidadLH = int(capacidadLH) - int(operadoresLH)
        capacidadRH = int(capacidadRH) - int(operadoresRH)

        estaciones.append([estacion, capacidadLH, operadoresLH, capacidadRH, operadoresRH, nombre_operadores_LH, nombre_operadores_RH])

    employees_for_line = functions.get_employees_for_line(linea)
    employees_for_line = int(employees_for_line[0][1]) if employees_for_line else 0

    employees_necessary = int(functions.get_employees_necesary_for_line(linea)[0][0])

    print('Las estaciones son:', estaciones)

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

    return render_template('visualizaciones.html', **context)

@app.route('/changeLine')
def changeLine():
    line = request.args.get('line')
    # Create a cookie named 'linea' with the value of the selected line
    response = flask.make_response(redirect('/'))
    response.set_cookie('linea', line)
    return response

