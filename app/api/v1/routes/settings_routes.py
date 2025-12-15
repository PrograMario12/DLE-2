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

            if action and action.startswith('select_area'):
                with open('debug_log.txt', 'a', encoding='utf-8') as f:
                    f.write(f"\n--- SELECT AREA ACTION: {action} ---\n")
                    f.write(f"Form Keys: {list(request.form.keys())}\n")
                    all_ids = request.form.getlist('all_positions')
                    
                    for pid in all_ids:
                        if pid and pid.strip().isdigit():
                            key = f'position_status_{pid}'
                            val = request.form.get(key)
                            is_checked = val is not None
                            user_service.update_position_status(int(pid), is_checked)
                        else:
                            f.write(f"Date invalid PID: {pid}\n")
                
                # Determine Cookie Logic
                response = make_response(redirect(url_for('main.home')))
                
                parts = action.split('select_area_')
                if len(parts) > 1:
                    target_group = parts[1].lower()
                    if 'inyección' in target_group:
                        response.set_cookie('line', '-1')
                    elif 'metalizado' in target_group:
                        response.set_cookie('line', '-2')
                
                return response

            # Fallback / Default: Line Selection
            selected_line = request.form.get('line')
            response = make_response(redirect(url_for('main.home')))

            if selected_line:
                response.set_cookie('line', selected_line)

            return response

        # GET Logic
        with open('debug_log.txt', 'a', encoding='utf-8') as f:
            f.write("\n--- GET REQUEST ---\n")
            available_lines = user_service.get_all_lines_for_settings()
            f.write(f"Available lines count: {len(available_lines)}\n")

            grouped_lines: dict[str, list[dict]] = {}
            for line in available_lines:
                group = line.get("group") or "Otras"
                grouped_lines.setdefault(group, []).append(line)
            
            f.write(f"Groups found: {list(grouped_lines.keys())}\n")

            # Update specific groups with detailed status
            for special_group in ['Inyección', 'Metalizado']:
                found_key = next((k for k in grouped_lines.keys() if k.lower() == special_group.lower()), None)
                f.write(f"Looking for '{special_group}' -> Found key: '{found_key}'\n")
                
                if found_key:
                    detailed_lines = user_service.get_lines_with_position_status(special_group)
                    f.write(f"Detailed lines fetched for '{special_group}': {len(detailed_lines) if detailed_lines else 0}\n")
                    if detailed_lines:
                        grouped_lines[found_key] = detailed_lines
                    else:
                        f.write(f"WARNING: No detailed lines for {special_group}\n")
                else:
                    f.write(f"WARNING: Group {special_group} not found in {list(grouped_lines.keys())}\n")

            return render_template("ajustes.html", grouped_lines=grouped_lines)

    @settings_bp.route('/general-exit', methods=['POST'])
    def general_exit():
        """
        Ejecuta la salida general para una línea específica.
        Espera un JSON con { "line_id": int }.
        """
        try:
            data = request.get_json()
            line_id = data.get('line_id')
            if not line_id:
                return {"success": False, "message": "ID de línea no proporcionado"}, 400
            
            count = user_service.perform_line_logout(int(line_id))
            
            return {
                "success": True, 
                "message": f"Salida registrada exitosamente.",
                "count": count
            }, 200
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

    return settings_bp
