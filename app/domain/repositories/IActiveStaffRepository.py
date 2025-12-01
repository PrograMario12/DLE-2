from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from app.domain.entities.active_staff import ActiveStaff

class IActiveStaffRepository(ABC):
    """Interfaz (contrato) para el repositorio de el personal activo
    (DIP)."""

    @abstractmethod
    def get_paginated(self, page: int, per_page: int, search_query: Optional[str] = None, 
                      sort_by: str = 'id', sort_order: str = 'asc', line_id: Optional[int] = None) -> Tuple[List[ActiveStaff], int]:
        pass

    @abstractmethod
    def get_all_active(self) -> List[ActiveStaff]:
        pass
