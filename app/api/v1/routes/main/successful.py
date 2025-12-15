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
import logging

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
        logger = logging.getLogger(__name__)

        employee_number_raw = request.cookies.get("employee_number")
        if not employee_number_raw or not employee_number_raw.isdigit() or int(
                employee_number_raw) <= 0:
            logger.error("Cookie 'employee_number' inválida: %s",
                         employee_number_raw)
            return redirect(url_for("main.home"))

        # 1) Validar cookie de empleado
        try:
            data = EmployeeCookie.model_validate(
                {"employee_number": employee_number_raw})
        except ValueError as e:
            logger.error("Error de validación de cookie: %s", e)
            return redirect(url_for("main.home"))

        side_id = request.args.get("id", type=int)
        logger.info("EN SUCCESSFUL: side_id recibido = %s", side_id)
        
        if side_id:
            try:
                user_service.register_entry_or_assignment(
                    employee_number=data.employee_number,
                    side_id=side_id,
                )
            except Exception as e:
                logger.error("Error al registrar entrada: %s", e)
                traceback.print_exc()
                return redirect(url_for("main.home"))
        else:
            try:
                user_service.register_entry_or_assignment(
                    employee_number=data.employee_number
                )
            except Exception as e:
                traceback.print_exc()

        try:
            info = user_service.get_user_info_for_display(data.employee_number) or {}
        except Exception as e:
            print("Error al obtener info de usuario:", e, file=sys.stderr)
            traceback.print_exc()

        try:
            display = station_service.get_user_status_for_display(
                int(data.employee_number)
            ) or {}
        except Exception as e:
            print("Error al obtener estado para display:", e, file=sys.stderr)
            traceback.print_exc()
            display = {}

        print(display)

        # 4) Resolver imagen
        image_filename = display.get("image")
        if not image_filename and "id" in info:
            image_filename = f"{info['id']}.png"

        import os
        from flask import current_app

        image_url = None
        if image_filename:
             # Construir ruta absoluta para verificar existencia
             static_folder = current_app.static_folder or "app/static"
             media_path = os.path.join(static_folder, "img", "media", image_filename)
             
             if os.path.exists(media_path):
                 image_url = url_for("static", filename=f"img/media/{image_filename}")
             else:
                 # Si no existe, dejamos image_url en None para activar el placeholder
                 logger.warning("Imagen no encontrada: %s", media_path)

        # 5) Contexto unificado
        ctx: Dict[str, Any] = {
            "css_href": url_for("static", filename="css/styles.css"),
            "user": info.get("name"),
            "line": display.get("line_name"),
            "station": display.get("station_name"),
            "tipo": display.get("type"),
            "color_class": display.get("color"),
            "image": image_url,
            "message": "¡Bienvenido, buen turno!" if display.get("type") == "Entrada" else "Gracias por tu esfuerzo hoy.",
            "animation_type": "anim-entry" if display.get("type") == "Entrada" else "anim-exit",
        }

        return render_template("successful.html", **ctx)
