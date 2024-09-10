''' This module contains the routes for the dashboards of the app. '''

from flask import Blueprint, render_template, request
from app import functions

dashboards_bp = Blueprint('settings', __name__)

@dashboards_bp.route('/visualizaciones')
def dashboard_lines():
    ''' Renders the dashboard page for the lines. '''
    results = functions.get_lines()
    number_of_lines = len(results)
    employees_for_line = functions.get_employees_for_line()
    employees_for_line = {line[0]: line[1] for line in
                          employees_for_line}

    there_are_no_lines = []

    lines = []

    for result in results:
        line = [result[1], result[2]]
        if result[1] in employees_for_line:
            line.append(employees_for_line[result[1]])
        else:
            line.append(0)

        lines.append(line)

    context = {
        'css_file': 'static/css/styles.css',
        'selection_type': 'línea',
        'num_cards': number_of_lines,
        'inline_operator_capacity': lines,
        'lineas': there_are_no_lines
    }

    return render_template('visualizaciones.html', **context)

@dashboards_bp.route('/visualizaciones_estación')
def dashboard_stations():
    ''' Renders the dashboard page for the stations. '''
    line = request.args.get('line')
    line_name = functions.get_line_id(line)

    results = functions.get_stations(line_name)
    numbers_of_stations = len(results)

    employees_for_station = functions.get_employees_for_station(line)
    employees_for_station = {station[0]: station[1] for station
                             in employees_for_station}
    stations_list = sorted(list(set([result[0] for result in results])))

    stations = prepare_stations_data(results, employees_for_station,
                                     line)

    employees_for_line = get_employees_for_line(line)
    employees_necessary = int(
            functions.get_employees_necessary_for_line(line)[0][0]
        )

    context = {
        'css_file': 'static/css/styles.css',
        'selection_type': 'estación',
        'num_cards': numbers_of_stations,
        'inline_operator_capacity': stations,
        'lineas': stations_list,
        'selected_line': line,
        'employees_for_line': employees_for_line,
        'employees_necessary': employees_necessary
    }

    return render_template('visualizaciones.html', **context)


def prepare_stations_data(results, employees_for_station, line):
    ''' Prepares the data for the stations. '''
    stations = []
    for result in results:
        station = result[0]
        capacity_lh, operators_lh = get_capacity_operators(
                                                result[1],
                                                station,
                                                employees_for_station,
                                                ' LH'
                                            )
        capacity_rh, operators_rh = get_capacity_operators(
                                                result[2],
                                                station,
                                                employees_for_station,
                                                ' RH'
                                            )

        names_operators_lh = functions.get_names_operators(
                                                station,
                                                line,
                                                'LH'
                                            )
        names_operators_rh = functions.get_names_operators(
                                                station,
                                                line,
                                                'RH'
                                            )

        stations.append([station, capacity_lh, operators_lh,
                         capacity_rh, operators_rh, names_operators_lh,
                         names_operators_rh])

    return stations


def get_capacity_operators(capacity, station, employees_for_station,
                           suffix):
    ''' Gets the capacity and operators for a station. '''
    operators = employees_for_station.get(f"{station}{suffix}", 0)
    capacity = int(capacity) - int(operators)
    return capacity, operators


def get_employees_for_line(line):
    ''' Gets the employees for a line. '''
    employees_for_line = functions.get_employees_for_line(line)
    return int(employees_for_line[0][1]) if employees_for_line else 0
