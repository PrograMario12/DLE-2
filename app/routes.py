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
        print("El tipo de registro es salida")
        return redirect('/exito')

    resultados = functions.obtener_lineas()
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

@app.route('/menuEstacion')
def menuEstacion():
    """
    Renders the menu page for selecting a station.

    Retrieves the employee number from the request arguments and sets it in the user object.
    Obtains the type of registration for the employee and redirects to the success page if the type is 'Salida'.
    Retrieves the line name from the user object and obtains the line ID.
    Sets the line name in the user object.
    Retrieves the stations for the line and calculates the number of stations.
    Retrieves the number of employees per station and creates a dictionary with station names as keys and employee counts as values.
    Sorts the list of station names and initializes an empty list for storing station information.
    Iterates over the results and extracts the station name, LH capacity, LH operators, RH capacity, and RH operators.
    Calculates the available LH and RH capacities by subtracting the number of LH and RH operators from the respective capacities.
    Appends the station information to the list of stations.
    Creates a context dictionary with CSS file path, selection type, number of stations, station capacities and operators, line names, and selected line.
    Renders the menu.html template with the context.
    """

    if 'linea' not in request.cookies:
        return redirect('/ajustes')

    numeroempleado = request.args.get('numeroempleado')
    print("Numero de empleado en Menú estación: " + numeroempleado)

    user.set_numero_empleado(numeroempleado)

    tipo = functions.get_last_register_type(user.numero_empleado)
    print("El tipo de registro es: " + tipo)
    if tipo == 'Exit':
        response = flask.make_response(redirect('/exito'))
        response.set_cookie('numeroempleado', numeroempleado)
        return response

    linea = request.cookies.get('linea')
    lineaname = functions.get_line_id(linea)
    user.set_linea(linea)

    resultados = functions.obtener_estaciones(lineaname)
    numero_estaciones = len(set([resultado[4] for resultado in resultados]))
    empleados_por_estacion = functions.get_employees_for_station(linea)
    empleados_por_estacion = {estacion[0]: estacion[1] for estacion in empleados_por_estacion}
    estacionesList = sorted(list(set([resultado[4] for resultado in resultados])))

    employees_for_line = functions.get_employees_for_line(request.cookies.get('linea'))[0][1] if functions.get_employees_for_line(user.linea) else 0
    employees_necessary = int(functions.get_employees_necesary_for_line(user.linea)[0][0])

    estaciones = [] 
    for i in range(0, len(resultados), 2):
        estacion = resultados[i][4]
        capacidadLH = resultados[i][2]
        operadoresLH = empleados_por_estacion.get(str(estacion) + " LH", 0)
        capacidadRH = resultados[i + 1][2]
        operadoresRH = empleados_por_estacion.get(str(estacion) + " RH", 0)
        
        capacidadLH = int(capacidadLH) - int(operadoresLH)
        capacidadRH = int(capacidadRH) - int(operadoresRH)

        estaciones.append([estacion, capacidadLH, operadoresLH, capacidadRH, operadoresRH])

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
    print("Numero de empleado en menuEstacion: " + request.cookies.get('numeroempleado'))

    return response


@app.route('/exito')
def exito():
    """
    This function is the route handler for the '/exito' endpoint.
    It retrieves the 'estacion' parameter from the request arguments and the current time.
    It sets the current time as the user's hora attribute.
    It then retrieves the usuario and imagen based on the user's numero_empleado.
    The imagen is converted to a file path.
    If the usuario is not found, it sets it to 'Error'.
    It retrieves the tipo of registro for the user.
    If the tipo is 'Entrada', it registers an entrada_salida with the user's information.
    Otherwise, it retrieves the linea and estacion from the previous salida and registers an entrada_salida with the updated information.
    Finally, it prepares the context with various variables and renders the 'exito.html' template with the context.
    """
    estacion = request.args.get('estacion')
    hora = datetime.now()
    user.set_hora(hora)

    print("Numero de empleado en éxito: " + request.cookies.get('numeroempleado'))

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
    lineas = functions.obtener_lineas()
    lineas_capacidad = [linea[1] for linea in lineas]

    context = {
        'css_file': 'static/css/styles.css',
        'num_botones': len(lineas_capacidad),
        'lineas': lineas_capacidad
    }

    return render_template('ajustes.html', **context)

@app.route('/visualizaciones')
def visualizaciones():

    resultados = functions.obtener_lineas()
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

    return render_template('visualizaciones.html', **context)

@app.route('/visualizacionesEstacion')
def visualizacionesEstacion():
    linea = request.args.get('linea')
    lineaname = functions.get_line_id(linea)
    resultados = functions.obtener_estaciones(lineaname)
    numero_estaciones = len(set([resultado[4] for resultado in resultados]))
    empleados_por_estacion = functions.get_employees_for_station(linea)
    empleados_por_estacion = {estacion[0]: estacion[1] for estacion in empleados_por_estacion}
    estacionesList = sorted(list(set([resultado[4] for resultado in resultados])))

    estaciones = [] 
    for i in range(0, len(resultados), 2):
        estacion = resultados[i][4]
        capacidadLH = resultados[i][2]
        operadoresLH = empleados_por_estacion.get(str(estacion) + " LH", 0)
        capacidadRH = resultados[i + 1][2]
        operadoresRH = empleados_por_estacion.get(str(estacion) + " RH", 0)
        
        capacidadLH = int(capacidadLH) - int(operadoresLH)
        capacidadRH = int(capacidadRH) - int(operadoresRH)

        estaciones.append([estacion, capacidadLH, operadoresLH, capacidadRH, operadoresRH])

    context = {
        'css_file': 'static/css/styles.css',
        'tipo_seleccion': 'estación',
        'num_cards': numero_estaciones,
        'lineas_capacidad_operadores': estaciones,
        'lineas': estacionesList,
        'lineaseleccionada': linea
    }

    return render_template('visualizaciones.html', **context)

@app.route('/changeLine')
def changeLine():
    line = request.args.get('line')
    # Create a cookie named 'linea' with the value of the selected line
    response = flask.make_response(redirect('/'))
    response.set_cookie('linea', line)
    return response