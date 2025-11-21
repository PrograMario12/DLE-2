from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from app.domain.entities.user import User, StationInfo

class IUserRepository(ABC):
    """Interfaz (contrato) para el repositorio de usuarios (DIP)."""

    @abstractmethod
    def find_user_by_card_number(self, card_number: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_last_register_type(self, card_number: int) -> Optional[str]:
        pass

    @abstractmethod
    def get_last_station_for_user(self, user_id: int) -> StationInfo:
        pass

    @abstractmethod
    def get_station_cards_for_line(self, line_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene los datos estructurados para las tarjetas de estaciones de una línea.
        """
        pass

    @abstractmethod
    def get_all_lines(self) -> list[dict]:
        """Obtiene una lista de todas las líneas de producción."""
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca un usuario por su ID primario."""
        pass

    def get_all_lines_summary(self) -> list[dict]:
        """
        Obtiene un resumen de todas las líneas de producción
        """
        pass

    def get_active_operators(self, station_id: int) -> list:
        """
        Obtiene una lista de operadores activos en una estación específica.
        """
        pass

    @abstractmethod
    def register_entry_or_assignment(self, user_id: int, side_id: int) -> None:
        """
        Persiste el registro de entrada/asignación para un usuario en un side (posición).
        Si el usuario tiene un registro abierto (exit_hour IS NULL), lo cierra (marca salida).
        Si no lo tiene, crea un nuevo registro de entrada en el side indicado.
        """
        pass