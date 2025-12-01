"""
src/domain/services/user_service.py
Servicio para la lógica de negocio relacionada con usuarios.
"""

from app.domain.repositories.IUserRepository import IUserRepository
from app.domain.repositories.IProductionLinesRepository import IProductionLinesRepository
from app.domain.repositories.IRegisterRepository import IRegisterRepository
from typing import Optional

class UserService:
    """
    Servicio para la lógica de negocio relacionada con usuarios.

    Este servicio actúa como intermediario entre la capa de presentación y la
    capa de acceso a datos, delegando las operaciones relacionadas con usuarios
    al repositorio inyectado. Implementa la lógica de negocio específica para
    usuarios, como el formato de datos y validaciones.
    """

    def __init__(self, user_repo: IUserRepository, 
                 production_line_repo: IProductionLinesRepository,
                 register_repo: IRegisterRepository):
        """
        Inicializa el servicio con un repositorio de usuarios.

        :param user_repo: Instancia de un repositorio que implementa la interfaz
                          IUserRepository, utilizada para acceder a los datos
                          relacionados con usuarios.
        """
        self._user_repo = user_repo
        self._production_line_repo = production_line_repo
        self._register_repo = register_repo

    def get_user_info_for_display(self, card_number: int) -> dict:
        """
        Obtiene y formatea la información de un usuario para la pantalla de éxito.

        :param card_number: Número de tarjeta del usuario.
        :return: Un diccionario con el nombre completo del usuario y su ID. Si el
                 usuario no está registrado, devuelve un mensaje predeterminado.
        """
        user = self._user_repo.find_user_by_card_number(card_number)
        if not user:
            return {'name': 'Usuario aún no registrado', 'id': None}

        return {'name': user.full_name, 'id': user.id}

    def get_all_lines_for_settings(self) -> list[dict]:
        """
        Obtiene la lista de líneas para mostrar en la página de configuración.

        :return: Una lista de diccionarios que representan las líneas disponibles.
        """
        return self._production_line_repo.get_all_lines()

    def get_user_last_register_type(self, card_number: int) -> Optional[str]:
        """
        Obtiene el tipo del último registro de un empleado.

        :param card_number: Número de tarjeta del usuario.
        :return: El tipo del último registro como cadena, o None si no hay registros.
        """
        return self._register_repo.get_last_register_type(card_number)

    def register_entry_or_assignment(self, employee_number: int,
                                     side_id: int = 0) -> None:
        """
        Registra la entrada o asignación del operador en la estación/side indicado.

        :param employee_number: Número de empleado asociado al usuario.
        :param side_id: Identificador de la estación o side donde se registra la entrada.
        :raises ValueError: Si el empleado no es encontrado en el repositorio.
        """
        self._register_repo.register_entry_or_assignment(user_id=employee_number,
                                                         side_id=side_id)

    def get_line_name_by_id(self, line_int: int) -> Optional[str]:
        return self._production_line_repo.get_line_name_by_id(line_int)