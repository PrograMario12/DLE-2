"""
    src/api/v1/routes/settings_routes.py
    Rutas para la configuración de línea y estación.
"""

from flask import Blueprint, render_template, request, make_response, redirect, \
    url_for  # Se importan utilidades de Flask para estructurar rutas, manejar peticiones y respuestas, y facilitar la navegación.

from app.domain.services.user_service import \
    UserService  # Se importa el servicio de usuario para delegar la lógica de negocio y mantener el código desacoplado.


def create_settings_bp(user_service: UserService) -> Blueprint:
    """
    Crea y configura el blueprint de configuración.

    Args:
        user_service (UserService): Servicio para manejar la lógica de negocio relacionada con usuarios.

    Returns:
        Blueprint: El blueprint de configuración con sus rutas registradas.
    """
    settings_bp = Blueprint('settings', __name__,
                            url_prefix='/settings')  # Se crea un Blueprint para modularizar las rutas y facilitar su mantenimiento.

    @settings_bp.route('/', methods=['GET',
                                     'POST'])  # Se define la ruta principal para configuración, permitiendo tanto consultas como envíos de datos.
    def configure_line_and_station():
        """
        Gestiona la selección de línea y estación por parte del usuario.

        Métodos:
            - GET: Muestra las opciones de líneas disponibles.
            - POST: Guarda la línea seleccionada en una cookie y
            redirige a la página principal.

        Returns:
            - En GET: Renderiza la plantilla 'ajustes.html' con las
            líneas disponibles.
            - En POST: Redirige a la página principal con la línea
            seleccionada almacenada en una cookie.
        """
        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'save_positions':
                # Logic to update toggles
                all_ids = request.form.getlist('all_positions')
                for pid in all_ids:
                    is_checked = request.form.get(f'position_status_{pid}') is not None
                    user_service.update_position_status(int(pid), is_checked)
                
                # Reload page to show changes
                return redirect(url_for('settings.configure_line_and_station'))

            # Fallback / Default: Line Selection
            selected_line = request.form.get('line')
            response = make_response(redirect(url_for('main.home')))

            if selected_line:
                response.set_cookie('line', selected_line)

            return response

        # GET Logic
        available_lines = user_service.get_all_lines_for_settings()

        grouped_lines: dict[str, list[dict]] = {}
        for line in available_lines:
            group = line.get("group") or "Otras"
            grouped_lines.setdefault(group, []).append(line)

        # Update specific groups with detailed status
        # Note: keys in grouped_lines come from DB (business_unit.bu_name)
        # We need to match precise naming.
        # Typically: 'Inyección', 'Metalizado', 'Ensamble'
        for special_group in ['Inyección', 'Metalizado']:
            # Check if group exists in fetched lines (case sensitive check usually required for dict keys)
            # We try to find the key case-insensitively just in case
            found_key = next((k for k in grouped_lines.keys() if k.lower() == special_group.lower()), None)
            
            if found_key:
                # Fetch enriched data
                detailed_lines = user_service.get_lines_with_position_status(special_group)
                if detailed_lines:
                    grouped_lines[found_key] = detailed_lines

        return render_template("ajustes.html", grouped_lines=grouped_lines)

    return settings_bp
