''' This module contains the routes for the dashboards of the app. '''

from flask import Blueprint, render_template, request
from app.model import dashboard_model

dashboards_bp = Blueprint('dashboards', __name__)

@dashboards_bp.route('/visualizaciones_lines')
def lines_dashboards():
    ''' Renders the dashboard page for the lines. '''
    dm = dashboard_model.LinesDashboard()
    lines = dm.create_lines_dashboard()

    context = {
        'lines': lines,
    }

    return render_template('lines_dashboards.html', **context)

@dashboards_bp.route('/dashboard_estaciones')
def stations_dashboard():
    ''' Renders the dashboard page for the stations. '''
    line = request.args.get('line')
    dm = dashboard_model.StationsDashboard()
    card_data = dm.create_stations_dashboard(line)
    name_line = dm.get_line(line)

    context = {
        'line': name_line,
        'cards': card_data
    }

    return render_template('stations_dashboards.html', **context)

@dashboards_bp.route('/get_operators_actives')
def get_operators_actives():
    ''' Get the operators actives '''
    station = request.args.get('id')
    print(station)

    dm = dashboard_model.OperatorsDashboard()
    operators = dm.get_operators(station)

    return operators
