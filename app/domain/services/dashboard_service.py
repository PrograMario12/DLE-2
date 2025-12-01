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
        Prepara los detalles de las estaciones para una línea específica.

        Args:
            line_id (int): El identificador único de la línea.

        Returns:
            dict: Un diccionario que contiene:
                - "line" (str): El nombre de la línea.
                - "cards" (list): Una lista de tarjetas asociadas a la línea.
                - "tipo" (str): El tipo de estación basado en la línea.
        """
        # Obtiene las tarjetas asociadas a la línea desde el repositorio de líneas
        cards = self._production_line_repo.get_station_cards_for_line(line_id)

        # Obtiene el nombre de la línea desde el repositorio de líneas
        line_name = self._production_line_repo.get_line_name_by_id(line_id)

        # Retorna un diccionario con los detalles de la línea y las estaciones asociadas
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