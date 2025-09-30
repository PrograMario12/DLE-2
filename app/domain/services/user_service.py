"""
src/domain/services/user_service.py
Servicio para la lógica de negocio relacionada con usuarios.
"""
from app.domain.repositories.user_repository import IUserRepository
from typing import Optional

class UserService:
    """Servicio para la lógica de negocio relacionada con usuarios."""

    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo

    def get_user_info_for_display(self, card_number: int) -> dict:
        """
        Obtiene y formatea la información de un usuario para la pantalla
        de éxito.
        """
        user = self._user_repo.find_user_by_card_number(card_number)
        if not user:
            return {'name': 'Usuario aún no registrado', 'id': None}

        return {'name': user.full_name, 'id': user.id}

    def get_all_lines_for_settings(self) -> list[dict]:
        """
        Obtiene la lista de líneas para mostrar en la página de configuración.
        """
        return self._user_repo.get_all_lines()

    def get_user_last_register_type(self, card_number: int) -> Optional[str]:
        """
        Obtiene el tipo del último registro de un empleado.
        """
        return self._user_repo.get_last_register_type(card_number)

    def register_entry_or_assignment(self, employee_number: int,
                                     side_id: int) -> None:
        """
        Registra la entrada o asignación del operador en la estación/side indicado.
        La implementación concreta se delega al repositorio.
        """
        # 1) Resolver el usuario por tarjeta
        user = self._user_repo.find_user_by_card_number(employee_number)
        if not user:
            raise ValueError("Empleado no encontrado")

        # 2) Delegar la persistencia (el repo debe implementar esta operación)
        self._user_repo.register_entry_or_assignment(user_id=user.id,
                                                     side_id=side_id)