# app/domain/services/production_lines_service.py

from app.domain.repositories.IProductionLinesRepository import IProductionLinesRepository
from typing import Optional, Any, List

class ProductionLinesService:
    """
    Servicio para la lógica de negocio relacionada con líneas de producción.

    Actúa como intermediario entre la capa de presentación y la capa de acceso a datos,
    delegando las operaciones al repositorio inyectado.
    """

    def __init__(self, lines_repo: IProductionLinesRepository):
        """
        Inicializa el servicio con un repositorio de líneas de producción.

        :param lines_repo: Instancia que implementa IProductionLinesRepository.
        """
        self._lines_repo = lines_repo

    def get_all_zones(self) -> List[Any]:
        """
        Obtiene todas las zonas de producción.

        :return: Lista de zonas.
        """
        return self._lines_repo.get_all_zones()

    def get_line_by_id(self, line_id: int) -> Optional[Any]:
        """
        Obtiene la línea de producción por su ID.

        :param line_id: Identificador de la línea.
        :return: La línea encontrada o None.
        """
        return self._lines_repo.get_line_by_id(line_id)

    def get_line_name_by_id(self, line_id: int) -> Optional[str]:
        """
        Obtiene el nombre completo de una línea por su ID.

        :param line_id: Identificador de la línea.
        :return: Nombre completo o None.
        """
        return self._lines_repo.get_line_name_by_id(line_id)