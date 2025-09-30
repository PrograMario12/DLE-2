"""GET /successful — Vista de éxito con datos del usuario."""
from flask import Blueprint, render_template, request, url_for, redirect
from app.domain.services.user_service import UserService
from app.api.v1.schemas.main import EmployeeCookie

def register_successful(bp: Blueprint, user_service: UserService) -> None:
    """
    Registra la ruta `/successful` en el blueprint proporcionado.

    Esta función define una vista que muestra una página de éxito con información
    del usuario. Si se proporciona un `side_id` como parámetro en la URL, se registra
    la asignación o entrada del usuario en la base de datos.

    :param bp: Instancia de `Blueprint` donde se registrará la ruta.
    :param user_service: Instancia de `UserService` para manejar la lógica de negocio
                         relacionada con usuarios.
    """
    @bp.get("/successful", endpoint="successful")
    def successful():
        """
        Vista para la ruta `/successful`.

        Esta vista realiza las siguientes acciones:
        - Valida la cookie `employee_number` para obtener los datos del empleado.
        - Si se proporciona un `side_id` en los parámetros de la URL, registra la
          asignación o entrada del usuario en la base de datos.
        - Obtiene la información del usuario para mostrarla en la página de éxito.
        - Renderiza la plantilla `successful.html` con los datos del usuario.

        :return: Respuesta HTTP con la página renderizada o redirección a `/home` en caso
                 de error.
        """
        try:
            # Valida la cookie para obtener el número de empleado
            data = EmployeeCookie.model_validate(
                {"employee_number": request.cookies.get("employee_number", "0")}
            )
        except Exception:
            # Redirige a la página principal si la validación falla
            return redirect(url_for("main.home"))

        # Si se proporciona un `side_id`, registra la asignación en la base de datos
        side_id = request.args.get("id", type=int)
        if side_id:
            # Manejo de excepciones al registrar la asignación
            import traceback, sys
            try:
                user_service.register_entry_or_assignment(
                    employee_number=data.employee_number,
                    side_id=side_id
                )
            except Exception as e:
                # Imprime el error y redirige a la página principal
                print("Error al registrar asignación:", e, file=sys.stderr)
                traceback.print_exc()
                return redirect(url_for("main.home"))

        # Obtiene la información del usuario para mostrar en la página
        info = user_service.get_user_info_for_display(data.employee_number)
        ctx = {
            "css_href": url_for("static", filename="css/styles.css"),
            "user": info["name"],
            "image": url_for("static", filename=f"img/media/{info['id']}.png"),
        }
        # Renderiza la plantilla con el contexto
        return render_template("successful.html", **ctx)