# app/domain/repositories/IProductionLinesRepository.py
from abc import ABC, abstractmethod
from typing import Any, List, Optional

class IProductionLinesRepository(ABC):
    @abstractmethod
    def get_all_zones(self) -> List[Any]:
        """Devuelve todas las zonas de producción."""
        pass

    @abstractmethod
    def get_line_by_id(self, line_id: int) -> Optional[Any]:
        """Devuelve la línea de producción por su ID."""
        pass