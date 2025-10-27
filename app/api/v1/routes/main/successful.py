"""
GET /successful — Vista de éxito con datos del usuario y su
estado/asignación.

app/api/v1/routes/main/successful.py
"""
from typing import Any, Dict
from flask import Blueprint, render_template, request, url_for, redirect
from app.domain.services.user_service import UserService
from app.domain.services.station_service import StationService
from app.api.v1.schemas.main import EmployeeCookie
import traceback, sys

def register_successful(
    bp: Blueprint,
    user_service: UserService,
    station_service: StationService,
) -> None:
    """
    Registra la ruta `/successful` en el blueprint proporcionado.

    - Valida cookie `employee_number`.
    - Si viene `?id=...`, registra asignación/entrada.
    - Combina info de usuario (UserService) y de pantalla/estado (StationService).
    - Renderiza `successful.html`.
    """

    @bp.route("/successful", methods=["GET", "POST"], endpoint="successful")
    def successful():
        # 1) Validar cookie de empleado
        try:
            data = EmployeeCookie.model_validate(
                {"employee_number": request.cookies.get("employee_number", "0")}
            )
        except Exception:
            return redirect(url_for("main.home"))

        side_id = request.args.get("id", type=int)
        if side_id:
            try:
                user_service.register_entry_or_assignment(
                    employee_number=data.employee_number,
                    side_id=side_id,
                )
            except Exception as e:
                print("Error al registrar asignación:", e, file=sys.stderr)
                traceback.print_exc()
                return redirect(url_for("main.home"))

        try:
            info = user_service.get_user_info_for_display(data.employee_number) or {}
        except Exception as e:
            print("Error al obtener info de usuario:", e, file=sys.stderr)
            traceback.print_exc()
            info = {}

        try:
            display = station_service.get_user_status_for_display(
                int(data.employee_number)
            ) or {}
        except Exception as e:
            print("Error al obtener estado para display:", e, file=sys.stderr)
            traceback.print_exc()
            display = {}

        # 4) Resolver imagen: prioriza la venida de display; si no, usa id de usuario
        image_filename = display.get("image")
        if not image_filename and "id" in info:
            image_filename = f"{info['id']}.png"

        # 5) Contexto unificado (mantiene claves de ambas implementaciones)
        ctx: Dict[str, Any] = {
            # ambos nombres para compatibilidad con tu plantilla
            "css_href": url_for("static", filename="css/styles.css"),
            "css_file": url_for("static", filename="css/styles.css"),
            "user": display.get("user") or info.get("name"),
            "line": display.get("line_name"),
            "station": display.get("station_name"),
            "tipo": display.get("type"),
            "color_class": display.get("color"),
            "image": (
                url_for("static", filename=f"img/media/{image_filename}")
                if image_filename
                else None
            ),
        }

        return render_template("successful.html", **ctx)
