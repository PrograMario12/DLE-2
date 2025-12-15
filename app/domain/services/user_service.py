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
    def get_lines_with_position_status(self, group_name: str) -> list[dict]:
        return self._production_line_repo.get_lines_with_position_status(group_name)

    def update_position_status(self, position_id: int, is_true: bool) -> None:
        self._production_line_repo.update_position_status(position_id, is_true)

    def perform_line_logout(self, line_id: int) -> int:
        """
        Realiza la salida general de todo el personal activo en una línea.
        :param line_id: ID de la línea.
        :return: Número de registros actualizados.
        """
        return self._register_repo.logout_active_users_in_line(line_id)

    def get_station_cards_for_line(self, line_id: int) -> list[dict]:
        return self._production_line_repo.get_station_cards_for_line(line_id)

    def create_side(self, position_id: int, title: str, capacity: int) -> int:
        return self._production_line_repo.create_side(position_id, title, capacity)

    def update_side(self, side_id: int, title: str, capacity: int) -> None:
        self._production_line_repo.update_side(side_id, title, capacity)

    def delete_side(self, side_id: int) -> None:
        self._production_line_repo.delete_side(side_id)

    def update_position(self, position_id: int, new_name: str) -> None:
        self._production_line_repo.update_position(position_id, new_name)

    def delete_position(self, position_id: int) -> None:
        self._production_line_repo.delete_position(position_id)

    def create_position(self, line_id: int, name: str) -> int:
        return self._production_line_repo.create_position(line_id, name)
