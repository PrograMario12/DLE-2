from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.user import StationInfo

class IRegisterRepository(ABC):
    """Interfaz para el repositorio de registros (fichajes)."""

    @abstractmethod
    def get_last_register_type(self, card_number: int) -> str:
        """Obtiene el tipo del último registro (Entry o Exit) de un empleado."""
        pass

    @abstractmethod
    def get_last_station_for_user(self, user_id: int) -> Optional[dict]:
        """Obtiene la última estación y línea donde el usuario realizó una entrada."""
        pass

    @abstractmethod
    def register_entry_or_assignment(self, user_id: int, side_id: int) -> None:
        """
        Persiste el registro de entrada/asignación para un usuario.
        Cierra registro abierto si existe, o crea uno nuevo.
        """
        pass
