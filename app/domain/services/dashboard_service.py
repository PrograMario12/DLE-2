from app.domain.repositories.IUserRepository import IUserRepository
from app.domain.repositories.IProductionLinesRepository import IProductionLinesRepository

class DashboardService:
    def __init__(self, user_repo: IUserRepository, production_line_repo: IProductionLinesRepository):
        self._user_repo = user_repo
        self._production_line_repo = production_line_repo

    def get_lines_summary(self) -> list[dict]:
        """Prepara el resumen de todas las líneas, incluyendo el porcentaje."""

        # 1. Obtiene los datos base del repositorio de líneas
        lines_from_repo = self._production_line_repo.get_all_lines_summary()

        processed_lines = []
        for line in lines_from_repo:
            operators = line.get('operators', 0)
            capacity = line.get('capacity', 0) or 0

            # 2. Calcula el porcentaje
            if capacity > 0:
                percentage = round((operators / capacity) * 100)
            else:
                percentage = 0  # Evita la división por cero si la capacidad es 0

            # 3. Añade el porcentaje y otros datos al nuevo diccionario
            line['percentage'] = percentage

            # (Opcional) Puedes añadir la lógica para la clase CSS aquí también
            if percentage < 99:
                line['class'] = 'employee-nook'  # Amarillo
            elif percentage > 100:
                line['class'] = 'employee-warning'  # Rojo
            else:
                line['class'] = 'employee-ok'  # Verde

            processed_lines.append(line)

        return processed_lines

    def get_station_details_for_line(self, line_id: int) -> dict:
        """
        Prepara los detalles de las estaciones para una línea o grupo específico.
        """
        if line_id < 0:
            # Logic for Groups (Inyección=-1, Metalizado=-2)
            group_name = "Inyección" if line_id == -1 else "Metalizado" if line_id == -2 else ""
            
            # Fetch config status
            lines_status = self._production_line_repo.get_lines_with_position_status(group_name)
            # Fetch operational data
            lines_summary = self._production_line_repo.get_all_lines_summary()
            
            # Map summary by ID
            summary_map = {l['id']: l for l in lines_summary}
            
            cards = []
            for l in lines_status:
                if l['is_visible']: # Only show enabled lines
                    # Restore summ definition for operators check
                    lid = l['id']
                    summ = summary_map.get(lid, {})
                    
                    # Use retrieved side_id and capacity (which might have been auto-created)
                    real_side_id = l.get('side_id')
                    real_capacity = l.get('capacity') or 0
                    operators = summ.get('operators') or 0 # Ops still come from summary until we link registers properly
                    
                    cards.append({
                        "position_name": l['name'],
                        "status": True,
                        "sides": [{
                            "side_id": real_side_id, 
                            "side_title": "BP", 
                            "name_side": "BP",
                            "employee_capacity": real_capacity,
                            "employees_working": operators
                        }], 
                        "is_afe": "afe" in l['name'].lower()
                    })
            
            return {
                "line": group_name,
                "cards": cards,
                "tipo": "Inyectora" if line_id == -1 else "Metalizadora"
            }

        # Original Logic
        cards = self._production_line_repo.get_station_cards_for_line(line_id)
        line_name = self._production_line_repo.get_line_name_by_id(line_id)

        return {
            "line": line_name,
            "cards": cards,
            "tipo": self._get_station_type_from_line(line_id)
        }

    def get_active_operators_for_station(self, station_id: int) -> list:
        """Obtiene los operadores activos para una estación."""
        return self._production_line_repo.get_active_operators(station_id)

    def _get_station_type_from_line(self, line_id: int) -> str:
        """Determina el nombre del tipo de estación basado en la línea."""
        if line_id == 6:
            return "Inyectora"
        if line_id == 7:
            return "Metalizadora"
        return "Estación"