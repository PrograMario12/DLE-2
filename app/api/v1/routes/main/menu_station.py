"""
app/api/v1/routes/main/menu_station.py
GET/POST /menuStation — Menú de estación por línea.
"""

from flask import Blueprint, render_template, request, make_response, redirect, url_for
from app.domain.services.user_service import UserService
from app.domain.services.dashboard_service import DashboardService
from app.api.v1.schemas.main import LineCookie, MenuStationForm

def register_menu_station(bp: Blueprint,
    user_service: UserService,
    dashboard_service: DashboardService) -> None:
    """
    Registra la ruta para el menú de estación en el blueprint proporcionado.

    Args:
        bp (Blueprint): El blueprint en el que se registrará la ruta.
        user_service (UserService): Servicio para manejar la lógica de
        negocio relacionada con usuarios.
        dashboard_service (DashboardService): Servicio para manejar la
        lógica de negocio relacionada con tableros.
    """
    @bp.route("/menuStation", methods=["GET", "POST"], endpoint="menu_station")
    def menu_station():
        """
        Maneja las solicitudes GET y POST para el menú de estación.

        Funcionalidad:
            - Valida la cookie 'line' utilizando el esquema LineCookie.
            - Redirige a la configuración de línea y estación si la
              cookie no es válida.
            - En solicitudes GET, redirige a la página de inicio.
            - En solicitudes POST:
                - Valida los datos del formulario utilizando el esquema
                  MenuStationForm.
                - Obtiene el último registro del usuario y redirige a la
                  vista de éxito si es de tipo 'Exit'.
                - Obtiene detalles de la estación para la línea
                  seleccionada y renderiza la plantilla 'menu.html'.

        Returns:
            Response: La respuesta HTTP con la plantilla renderizada, redirección o cookies configuradas.
        """
        # Obtiene y valida la cookie 'line'
        line_raw = request.cookies.get("line")

        if not line_raw:
            # Redirige si la cookie no está presente
            return redirect(url_for("settings.configure_line_and_station"))
        try:
            # Valida el contenido de la cookie
            line = LineCookie.model_validate({"line": line_raw}).line
        except Exception:
            # Redirige si la validación falla
            return redirect(url_for("settings.configure_line_and_station"))

        # Maneja solicitudes GET
        if request.method == "GET":
            return redirect(url_for("main.home"))

        # Valida los datos del formulario
        try:
            form = MenuStationForm.model_validate(dict(request.form))
        except Exception:
            # Redirige si la validación del formulario falla
            return redirect(url_for("main.home"))

        # Verifica el último registro del usuario
        last = user_service.get_user_last_register_type(form.employee_number)
        print("El último registro es:", last)
        if last == "Exit":
            # Redirige a la vista de éxito si el último registro es de tipo 'Exit'
            resp = make_response(redirect(url_for("main.successful")))
            resp.set_cookie("employee_number", str(form.employee_number), httponly=True, samesite="Lax")
            return resp

        # Obtiene detalles de la estación y renderiza la plantilla
        data = dashboard_service.get_station_details_for_line(line)

        # Calcula clases por side y por card, y totales para "Real" y "Fuera de estándar"
        cards = data.get("cards") or []

        def side_status_class(cap: int, act: int) -> str:
            """
            Determina la clase CSS para un lado basado en la capacidad y el número de empleados activos.

            Args:
                cap (int): Capacidad de empleados.
                act (int): Número de empleados activos.

            Returns:
                str: Clase CSS correspondiente.
            """
            if act < cap:
                return "employee-nook"      # falta personal (amarillo)
            elif act == cap:
                return "employee-ok"        # justo (verde)
            else:
                return "employee-warning"   # excede (rojo)

        total_capacity, total_active = 0, 0
        for card in cards:
            # Agregado por tarjeta
            card_cap, card_act = 0, 0
            for side in card.get("sides", []):
                cap = int(side.get("employee_capacity") or 0)
                act = int(side.get("employees_working") or 0)
                card_cap += cap
                card_act += act

                # Asigna clase de side si no viene definida
                if not side.get("class"):
                    side["class"] = side_status_class(cap, act)

            # Clase de fondo para la tarjeta grande, solo si está visible
            if card.get("status", True) is not False:
                if card_act < card_cap:
                    card["class"] = (card.get("class") or "") + " card--under"
                elif card_act == card_cap:
                    card["class"] = (card.get("class") or "") + " card--ok"
                else:
                    card["class"] = (card.get("class") or "") + " card--over"

                # Acumula totales globales
                total_capacity += card_cap
                total_active  += card_act

        # Prepara variables esperadas por el template
        data["cards"] = cards
        data["total_capacity"] = total_capacity       # Fuera de estándar
        data["total_employees"] = total_active        # Real

        # Renderiza la plantilla y configura cookies
        resp = make_response(render_template("menu.html", **data))
        resp.set_cookie("employee_number", str(form.employee_number), httponly=True, samesite="Lax")
        return resp


    @bp.route("/afeMenu", methods=["GET"], endpoint="afe_menu")
    def afe_menu():
        """
        Maneja la solicitud GET para el menú de actividades fuera de estándar (AFE).

        Funcionalidad:
            - Obtiene una lista de actividades fuera de estándar.
            - Renderiza la plantilla 'afe_menu.html' con las actividades y el ID del lado.

        Returns:
            Response: La respuesta HTTP con la plantilla renderizada.
        """
        # Lista de actividades fuera de estándar
        activities = [
            {"id": 1, "name": "Contenciones / Retrabajos"},
            {"id": 2, "name": "Entrenamiento esporádico"},
            {"id": 3, "name": "Pruebas de ingeniería / Corridas especiales"},
            {"id": 4, "name": "Juntas o reuniones especiales"},
        ]
        # Obtiene el ID del lado desde los parámetros de la solicitud
        side_id = request.args.get("side_id")
        # Renderiza la plantilla con las actividades y el ID del lado
        return render_template("afe_menu.html", activities=activities, side_id=side_id)