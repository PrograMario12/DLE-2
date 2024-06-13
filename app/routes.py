from app import app, functions
from flask import redirect
from app import app
from flask import redirect, render_template, request
from datetime import datetime


user = functions.Usuario(0, 0, 0)

@app.route("/")
def home():
    return render_template('index.html', css_file='static/css/stylesinicio.css', js_file='static/js/reloj.js')


@app.route('/menuLinea')
def menuLinea():
    numeroempleado = request.args.get('numeroempleado')
    user.set_numero_empleado(numeroempleado)

    tipo = functions.obtener_tipo_registro(user.numero_empleado)
    print("El tipo de registro es: ", tipo)
    if tipo == 'Salida':
        return redirect('/exito')

    resultados = functions.obtener_lineas()
    numero_lineas = len(resultados)
    empleados_por_linea = functions.obtener_empleados_por_linea()
    empleados_por_linea = {int(linea[0]): linea[1] for linea in empleados_por_linea}
    print("Los empleados por línea son: ", empleados_por_linea)
    no_hay_lineas = []

    lineas = []
    '''
        resultado[0] es igual al id de la línea
        resultado[2] es igual a la capacidad de la línea
    '''
    for resultado in resultados:
        linea = [resultado[0], resultado[2]]
        if resultado[0] in empleados_por_linea:
            linea.append(empleados_por_linea[resultado[0]])
        else:
            linea.append(0)

        #Aquí se calcula la cantidad de operadores disponibles
        linea[1] = int(linea[1]) - int(linea[2])

        #Aquí se agrega la línea a la lista de lineas
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
    linea = request.args.get('linea')
    user.set_linea(linea)

    resultados = functions.obtener_estaciones(linea)
    numero_estaciones = len(set([resultado[4] for resultado in resultados]))
    empleados_por_estacion = functions.obtener_empleados_por_estacion(linea)
    empleados_por_estacion = {estacion[0]: estacion[1] for estacion in empleados_por_estacion}
    estacionesList = sorted(list(set([resultado[4] for resultado in resultados])))

    

    estaciones = [] # [estacion, capacidad, operadores]
    for i in range(0, len(resultados), 2):
        estacion = resultados[i][4]
        capacidadLH = resultados[i][2]
        operadoresLH = empleados_por_estacion.get(str(estacion) + " LH", 0)
        capacidadRH = resultados[i + 1][2]
        operadoresRH = empleados_por_estacion.get(str(estacion) + " RH", 0)
        
        capacidadLH = int(capacidadLH) - int(operadoresLH)
        capacidadRH = int(capacidadRH) - int(operadoresRH)

        #Aquí se calcula la cantidad de operadores disponibles
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
    estacion = request.args.get('estacion')
    hora = datetime.now()
    user.set_hora(hora)


    usuario = functions.obtener_usuario(user.numero_empleado)
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
        'tipo': tipo
    }
    return render_template('exito.html', **context)