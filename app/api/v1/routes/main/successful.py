"""GET /successful — Vista de éxito con datos del usuario."""
from flask import Blueprint, render_template, request, url_for, redirect
from app.domain.services.user_service import UserService
from app.api.v1.schemas.main import EmployeeCookie

def register_successful(bp: Blueprint, user_service: UserService) -> None:
    @bp.get("/successful", endpoint="successful")
    def successful():
        try:
            data = EmployeeCookie.model_validate(
                {"employee_number": request.cookies.get("employee_number", "0")}
            )
        except Exception:
            return redirect(url_for("main.home"))

        # Si viene la selección de estación/side, registrar en BD aquí
        side_id = request.args.get("id", type=int)
        if side_id:
            # NO silencies la excepción: imprime el traceback
            import traceback, sys
            try:
                user_service.register_entry_or_assignment(
                    employee_number=data.employee_number,
                    side_id=side_id
                )
            except Exception as e:
                print("Error al registrar asignación:", e, file=sys.stderr)
                traceback.print_exc()
                return redirect(url_for("main.home"))

        info = user_service.get_user_info_for_display(data.employee_number)
        ctx = {
            "css_href": url_for("static", filename="css/styles.css"),
            "user": info["name"],
            "image": url_for("static", filename=f"img/media/{info['id']}.png"),
        }
        return render_template("successful.html", **ctx)
