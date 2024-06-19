from app import app, functions
from flask import redirect, render_template, request
from datetime import datetime


user = functions.Usuario(0, 0, 0)

@app.route("/")
def home():
    """
    Renders the home page.

    Returns:
        The rendered template for the home page with the specified CSS and JavaScript files.
    """

    context = {
        'css_file': 'static/css/stylesinicio.css',
        'js_file': 'static/js/reloj.js',
        'img_file': 'static/img/magna-logo.png'
    }
    

    return render_template('index.html', **context)


@app.route('/menuLinea')
def menuLinea():
    """
    Renders the menu page for selecting a line.

    This function retrieves the employee number from the request arguments,
    sets it in the user object, and then obtains the type of registration
    for the employee. If the type is 'Salida', it redirects to the '/exito'
    page. Otherwise, it retrieves the lines and the number of employees per
    line. It calculates the number of available operators for each line and
    constructs a list of lines with their capacity and available operators.
    Finally, it renders the 'menu.html' template with the necessary context.

    Returns:
        The rendered 'menu.html' template with the context.
    """
    numeroempleado = request.args.get('numeroempleado')
    user.set_numero_empleado(numeroempleado)

    tipo = functions.obtener_tipo_registro(user.numero_empleado)
    if tipo == 'Salida':
        return redirect('/exito')

    resultados = functions.obtener_lineas()
    numero_lineas = len(resultados)
    empleados_por_linea = functions.obtener_empleados_por_linea()
    empleados_por_linea = {int(linea[0]): linea[1] for linea in empleados_por_linea}
    no_hay_lineas = []

    lineas = []
    '''
        resultado[0] is equal to the line id
        resultado[2] is equal to the line capacity
    '''
    for resultado in resultados:
        linea = [resultado[0], resultado[2]]
        if resultado[0] in empleados_por_linea:
            linea.append(empleados_por_linea[resultado[0]])
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
    Renders the menu page for a specific station.

    Retrieves the selected line from the request arguments and sets it for the user.
    Obtains the stations and their information for the selected line.
    Calculates the number of stations, employees per station, and available operators for each station.
    Constructs the context for rendering the menu page.
    
    Returns:
        The rendered menu page with the constructed context.
    """
    linea = request.args.get('linea')
    user.set_linea(linea)

    resultados = functions.obtener_estaciones(linea)
    numero_estaciones = len(set([resultado[4] for resultado in resultados]))
    empleados_por_estacion = functions.obtener_empleados_por_estacion(linea)
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

    return render_template('menu.html', **context)

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

    usuario = functions.obtener_usuario(user.numero_empleado)
    imagen = functions.obtener_imagen(user.numero_empleado)
    imagen = 'static/img/media/' + str(imagen) + '.png'
    print("La imagen es: ", imagen)

    if not usuario:
        usuario = 'Error'

    tipo = functions.obtener_tipo_registro(user.numero_empleado)

    if tipo == 'Entrada':
        functions.registar_entrada_salida(user.numero_empleado, user.linea, estacion, tipo, hora)
        linea = user.linea
    else:
        linea_res = functions.obtener_valores_salida(user.numero_empleado)
        estacion = linea_res[1]
        linea = linea_res[0]
        functions.registar_entrada_salida(user.numero_empleado, linea, estacion, tipo, hora)

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