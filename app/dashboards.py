from flask import Blueprint, render_template, request
from app import functions

dashboards_bp = Blueprint('settings', __name__)

@dashboards_bp.route('/visualizaciones')
def dashboard_lines():
    results = functions.get_lines()
    number_of_lines = len(results)
    employees_for_line = functions.get_employees_for_line()
    employees_for_line = {line[0]: line[1] for line in 
                          employees_for_line}

    there_are_no_lines = []

    lines = []
    '''
        result[0] is equal to the line id
        result[2] is equal to the line capacity
    '''
    for result in results:
        line = [result[1], result[2]]
        if result[1] in employees_for_line:
            line.append(employees_for_line[result[1]])
        else:
            line.append(0)

        #Here we calculate the number of available operators
        # line[1] = int(line[1]) - int(line[2])

        #Here we check if the line has available operators
        lines.append(line)

    context = {
        'css_file': 'static/css/styles.css',
        'tipo_seleccion': 'línea',
        'num_cards': number_of_lines,
        'lineas_capacidad_operadores': lines,
        'lineas': there_are_no_lines
    }

    return render_template('visualizaciones.html', **context)

@dashboards_bp.route('/visualizacionesEstacion')
def dashboard_stations():
    line = request.args.get('line')
    line_name = functions.get_line_id(line)

    results = functions.get_stations(line_name)
    numbers_of_stations = len(results)

    employees_for_station = functions.get_employees_for_station(line)
    employees_for_station = {station[0]: station[1] for station in 
                             employees_for_station}
    stations_list = sorted(list(set([result[0] for result in results])))

    stations = []
    for result in results:
        station = result[0]
        capacity_LH = result[1]
        operators_LH = employees_for_station.get(str(station) 
                                                 + " LH", 0)
        capacity_RH = result[2]
        operators_RH = employees_for_station.get(str(station) 
                                                 + " RH", 0)

        names_operators_LH = functions.get_names_operators(station,
                                                           line, 'LH')

        names_operators_RH = functions.get_names_operators(station, 
                                                           line, 'RH')

        capacity_LH = int(capacity_LH) - int(operators_LH)
        capacity_RH = int(capacity_RH) - int(operators_RH)

        stations.append([station, capacity_LH, operators_LH, 
                         capacity_RH, operators_RH, names_operators_LH, 
                         names_operators_RH])

    employees_for_line = functions.get_employees_for_line(line)
    employees_for_line = (
        int(employees_for_line[0][1])
        if employees_for_line
        else 0
    )

    employees_necessary = int(functions.get_employees_necessary_for_line
                              (line)[0][0])

    print('Las stations son:', stations)

    context = {
        'css_file': 'static/css/styles.css',
        'tipo_seleccion': 'estación',
        'num_cards': numbers_of_stations,
        'lineas_capacidad_operadores': stations,
        'lineas': stations_list,
        'lineaseleccionada': line,
        'employees_for_line': employees_for_line,
        'employees_necessary': employees_necessary
    }

    return render_template('visualizaciones.html', **context)