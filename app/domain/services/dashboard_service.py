from typing import Dict, Any, List
from app.domain.repositories.user_repository import IUserRepository


class DashboardService:
    """
    Contiene la lógica de negocio para construir los datos de los dashboards.
    Depende de una interfaz de repositorio para obtener los datos (DIP).
    """

    def __init__(self, user_repo: IUserRepository):
        """Inyecta la dependencia del repositorio de usuarios."""
        self._user_repo = user_repo

    def prepare_station_dashboard(self, line_id: int) -> Dict[str, Any]:
        """
        Prepara todos los datos necesarios para la vista del dashboard de una línea.

        Args:
            line_id: El ID de la línea a consultar.

        Returns:
            Un diccionario con los datos listos para ser usados en la plantilla.
        """
        cards_data = self._user_repo.get_station_cards_for_line(line_id)
        line_name = self._user_repo.get_line_name_by_id(line_id)

        total_capacity = 0
        total_employees = 0

        for card in cards_data:
            if card.get('status'):
                for side in card.get('sides', []):
                    total_capacity += side.get('employee_capacity', 0)
                    total_employees += side.get('employees_working', 0)

        # El cálculo original era `max((total_capacity - 1) - total_employees, 0)`
        available_capacity = max(total_capacity - total_employees, 0)

        return {
            "cards": cards_data,
            "line_name": line_name or "Línea desconocida",
            "total_capacity": available_capacity,
            "total_employees": total_employees,
            "station_type": self._get_station_type_from_line(line_id),
        }

    def _get_station_type_from_line(self, line_id: int) -> str:
        """Determina el nombre del tipo de estación basado en la línea."""
        if line_id == 6:
            return "Inyectora"
        if line_id == 7:
            return "Metalizadora"
        return "Estación"