"""
Controladores para el endpoint /menuStation y /afeMenu.
app/api/v1/routes/main/menu_station/controllers.py
"""

from __future__ import annotations
from flask import (request, redirect, url_for, make_response,
                   render_template, flash)
from app.domain.services.user_service import UserService
from app.domain.services.dashboard_service import DashboardService
from .cookies import read_valid_line_cookie
from .validators import validate_menu_station_form
from .presenter import build_menu_view_model

def menu_station_post(*, user_service: UserService,
                      dashboard_service: DashboardService):
    """
    Maneja las solicitudes GET y POST al endpoint /menuStation.

    Args:
        user_service (UserService): Servicio para manejar la lógica relacionada con usuarios.
        dashboard_service (DashboardService): Servicio para manejar la lógica del dashboard.

    Returns:
        Response: Respuesta HTTP basada en la lógica del endpoint.

    Notas:
        - GET: Redirige al endpoint main.home.
        - POST: Valida el formulario, revisa el último registro del usuario y genera un ViewModel para la plantilla.
    """

    # 1) Validar cookie 'line' (redirigir si no es válida)
    line = read_valid_line_cookie()  # Lee y valida la cookie 'line'
    if line is None:
        return redirect(url_for("settings.configure_line_and_station"))  # Redirige si no es válida

    # 2) GET -> redirige a home (compatibilidad con comportamiento actual)
    form = validate_menu_station_form(request.form)  # Valida los datos del formulario

    if request.method == "GET" or form is None:
        flash("Ocurrió un error al procesar tu solicitud. "
              "Intenta de nuevo.",
              "error")
        return redirect(url_for("main.home"))

    # 4) Regla de negocio: si el último registro del usuario es "Exit" -> success
    # Este tiene problemas porque no está arrojando el exit
    last = user_service.get_user_last_register_type(form.employee_number)
    print(f"DEBUG_CONTROLLER: Last register type for {form.employee_number} is '{last}'")

    if last == "Exit":
        resp = make_response(redirect(url_for("main.successful")))
    else:
        data = dashboard_service.get_station_details_for_line(line)
        cards = data.get("cards") or []

        # Separar AFE y normales
        cards_main, cards_afe = [], []
        for card in cards:
            name = (card.get("position_name") or "")
            is_afe = bool(card.get("is_afe")) or ("afe" in name.lower())
            (cards_afe if is_afe else cards_main).append(card)

        has_afe = len(cards_afe) > 0

        # Puedes seguir usando tu build_menu_view_model si lo necesitas
        view_model = build_menu_view_model(data)
        view_model.update({
            "cards_main": cards_main,
            "cards_afe": cards_afe,
            "has_afe": has_afe
        })

        resp = make_response(render_template("menu.html", **view_model))

    # 5) ESTABLECER LA COOKIE (UN SOLO LUGAR)
    # No importa cuál fue la respuesta (redirect o render),
    # le establecemos la cookie.
    resp.set_cookie("employee_number", str(form.employee_number),
                    httponly=True,
                    samesite="Lax")
    return resp


def afe_menu_get():
    """
    Maneja las solicitudes GET al endpoint /afeMenu.

    Returns:
        Response: Renderiza la plantilla afe_menu.html con la lista de actividades y el side_id opcional.

    Notas:
        - Devuelve una lista de actividades predefinidas.
        - Incluye el parámetro opcional side_id obtenido de los argumentos de la solicitud.
    """
    side_id = request.args.get("side_id")

    print("El side_id es ", side_id)



    activities = [
        {"id": 1, "name": "Contenciones / Retrabajos"},
        {"id": 2, "name": "Entrenamiento esporádico"},
        {"id": 3, "name": "Pruebas de ingeniería / Corridas especiales"},
        {"id": 4, "name": "Juntas o reuniones especiales"},
    ]
    return render_template("afe_menu.html", activities=activities, side_id=side_id)
