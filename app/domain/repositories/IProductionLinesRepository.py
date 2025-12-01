from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class IProductionLinesRepository(ABC):
    """Interfaz para el repositorio de líneas de producción y estaciones."""

    @abstractmethod
    def get_all_lines(self) -> list[dict]:
        """Obtiene una lista de todas las líneas de producción."""
        pass

    @abstractmethod
    def get_all_lines_summary(self) -> list[dict]:
        """Obtiene un resumen de todas las líneas con sus operadores y capacidad."""
        pass

    @abstractmethod
    def get_station_cards_for_line(self, line_id: int) -> List[Dict[str, Any]]:
        """Obtiene los datos estructurados para las tarjetas de estaciones de una línea."""
        pass

    @abstractmethod
    def get_active_operators(self, station_id: int) -> list:
        """Obtiene una lista de operadores activos en una estación específica."""
        pass

    @abstractmethod
    def get_line_name_by_id(self, line_id: int) -> Optional[str]:
        """Obtiene el nombre completo de una línea dado su ID."""
        pass

    @abstractmethod
    def get_line_by_id(self, line_id: int) -> Optional[dict]:
        """Obtiene los detalles de una línea dado su ID."""
        pass