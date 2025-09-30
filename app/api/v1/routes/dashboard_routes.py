from flask import Blueprint, render_template, request, jsonify
from app.domain.services.dashboard_service import DashboardService

# El blueprint ahora tiene el prefijo /dashboards
dashboards_bp = Blueprint('dashboards', __name__, url_prefix='/dashboards')

# Placeholder para el servicio que será inyectado
dashboard_service: DashboardService


@dashboards_bp.route('/lines')
def show_lines_dashboard():
    """
    Renderiza la página principal que muestra el resumen de todas las
    líneas.
    (Reemplaza la antigua ruta /visualizaciones_lines)
    """

    lines_data = dashboards_bp.dashboard_service.get_lines_summary()
    return render_template('lines_dashboards.html', lines=lines_data)

@dashboards_bp.route('/stations')
def show_stations_dashboard():
    line_id = request.args.get('line', type=int)
    if not line_id:
        return "Error: Se requiere un ID de línea.", 400

    station_data = dashboards_bp.dashboard_service.get_station_details_for_line(line_id)
    cards = station_data.get('cards') or []

    # ---- Separar AFE vs no-AFE ----
    cards_main, cards_afe = [], []
    for card in cards:
        name = (card.get('position_name') or '')
        is_afe = bool(card.get('is_afe')) or ('afe' in name.lower())
        (cards_afe if is_afe else cards_main).append(card)

    # ---- Calcular clases por side y por card (agregado) ----
    def side_status_class(cap: int, act: int) -> str:
        if act < cap:
            return "employee-nook"      # amarillo (falta personal)
        elif act == cap:
            return "employee-ok"        # verde (justo)
        else:
            return "employee-warning"   # rojo (exceso)

    for card in cards:
        # set para cada side
        total_cap, total_act = 0, 0
        for side in card.get('sides', []):
            cap = int(side.get('employee_capacity') or 0)
            act = int(side.get('employees_working') or 0)
            total_cap += cap
            total_act += act
            # si ya traía una clase, respétala; si no, asígnala
            if not side.get('class'):
                side['class'] = side_status_class(cap, act)

        # clase de card agregada (para pintar el fondo de la tarjeta grande)
        if card.get('status', True) is not False:
            if total_act < total_cap:
                card['class'] = (card.get('class') or "") + " card--under"
            elif total_act == total_cap:
                card['class'] = (card.get('class') or "") + " card--ok"
            else:
                card['class'] = (card.get('class') or "") + " card--over"

    # ---- Totales (como ya tenías) ----
    total_capacity, total_active = 0, 0
    for card in cards:
        if card.get('status', True) is False:
            continue
        for side in card.get('sides', []):
            total_capacity += int(side.get('employee_capacity') or 0)
            total_active  += int(side.get('employees_working') or 0)

    if total_capacity > 0:
        pct_active = round((total_active / total_capacity) * 100)
        overflow = max(total_active - total_capacity, 0)
        overflow_pct = round((overflow / total_capacity) * 100) if overflow else 0
        pct_active_clamped = min(100, pct_active)
    else:
        pct_active_clamped, overflow_pct = 0, 0

    station_data['totals'] = {
        'capacity': total_capacity,
        'active': total_active,
        'pct_active': pct_active_clamped,
        'overflow_pct': overflow_pct,
    }
    station_data['cards_main'] = cards_main
    station_data['cards_afe']  = cards_afe
    station_data['has_afe']    = len(cards_afe) > 0

    return render_template('stations_dashboards.html', **station_data)



@dashboards_bp.route('/api/operators')
def get_active_operators():
    """
    Endpoint de API que devuelve los operadores activos para una estación.
    (Reemplaza la antigua ruta /get_operators_actives)
    """
    station_id = request.args.get('id', type=int)
    if not station_id:
        return jsonify({"error": "Se requiere un ID de estación."}), 400

    # Llama al servicio para obtener los datos y los devuelve como JSON
    operators = dashboards_bp.dashboard_service.get_active_operators_for_station(station_id)
    return jsonify(operators)