from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.user import User

class IActiveStaffRepository(ABC):
    """Interfaz (contrato) para el repositorio de el personal activo
    (DIP)."""

    @abstractmethod
    def get_all(self) -> List[User]:
        pass
