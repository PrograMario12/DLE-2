from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from app.domain.entities.active_staff import ActiveStaff

class IActiveStaffRepository(ABC):
    """Interfaz (contrato) para el repositorio de el personal activo
    (DIP)."""

    @abstractmethod
    def get_paginated(self, page: int, per_page: int, search_query: Optional[str] = None) -> Tuple[List[ActiveStaff], int]:
        pass
