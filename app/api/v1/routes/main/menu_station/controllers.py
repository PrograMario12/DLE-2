from __future__ import annotations
from flask import request, redirect, url_for, make_response, render_template
from app.domain.services.user_service import UserService
from app.domain.services.dashboard_service import DashboardService
from .cookies import read_valid_line_cookie
from .validators import validate_menu_station_form
from .presenter import build_menu_view_model

def menu_station_post(*, user_service: UserService,
                      dashboard_service: DashboardService):
    """Handler para GET/POST de /menuStation
    - GET: redirige a main.home
    - POST: valida form, revisa último registro y arma ViewModel para la plantilla
    """
    # 1) Validar cookie 'line' (redirigir si no es válida)
    line = read_valid_line_cookie()
    if line is None:
        return redirect(url_for("settings.configure_line_and_station"))

    # 2) GET -> redirige a home (compatibilidad con comportamiento actual)
    if request.method == "GET":
        return redirect(url_for("main.home"))

    # 3) Validar formulario (redirigir si no es válido)
    form = validate_menu_station_form(request.form)
    if form is None:
        return redirect(url_for("main.home"))

    # 4) Regla de negocio: si el último registro del usuario es "Exit" -> success
    last = user_service.get_user_last_register_type(form.employee_number)
    if last == "Exit":
        resp = make_response(redirect(url_for("main.successful")))
        resp.set_cookie("employee_number", str(form.employee_number), httponly=True,
                        samesite="Lax")
        return resp

    # 5) Obtener detalles de estación y transformar a ViewModel listo para la vista
    data = dashboard_service.get_station_details_for_line(line)
    view_model = build_menu_view_model(data)

    # 6) Render y cookie
    resp = make_response(render_template("menu.html", **view_model))
    resp.set_cookie("employee_number", str(form.employee_number), httponly=True,
                    samesite="Lax")
    return resp

def afe_menu_get():
    """GET /afeMenu: devuelve la lista de AFE y el side_id opcional."""
    activities = [
        {"id": 1, "name": "Contenciones / Retrabajos"},
        {"id": 2, "name": "Entrenamiento esporádico"},
        {"id": 3, "name": "Pruebas de ingeniería / Corridas especiales"},
        {"id": 4, "name": "Juntas o reuniones especiales"},
    ]
    side_id = request.args.get("side_id")
    return render_template("afe_menu.html", activities=activities, side_id=side_id)
