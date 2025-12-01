from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.user import User

class IUserRepository(ABC):
    """Interfaz para el repositorio de usuarios."""

    @abstractmethod
    def find_user_by_card_number(self, card_number: int) -> Optional[User]:
        """Busca un usuario por su número de tarjeta."""
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca un usuario por su ID primario."""
        pass