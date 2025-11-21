"""
src/domain/services/user_service.py
Servicio para la lógica de negocio relacionada con usuarios.
"""

from app.domain.repositories.user_repository import IUserRepository  # Se importa la interfaz para asegurar que el servicio dependa de una abstracción y no de una implementación concreta.
from typing import Optional  # Se importa Optional para tipar correctamente los retornos que pueden ser None y así mejorar la legibilidad y robustez.

class UserService:
    """
    Servicio para la lógica de negocio relacionada con usuarios.

    Este servicio actúa como intermediario entre la capa de presentación y la
    capa de acceso a datos, delegando las operaciones relacionadas con usuarios
    al repositorio inyectado. Implementa la lógica de negocio específica para
    usuarios, como el formato de datos y validaciones.
    """

    def __init__(self, user_repo: IUserRepository):
        """
        Inicializa el servicio con un repositorio de usuarios.

        :param user_repo: Instancia de un repositorio que implementa la interfaz
                          IUserRepository, utilizada para acceder a los datos
                          relacionados con usuarios.
        """
        self._user_repo = user_repo  # Se guarda el repositorio para que todas las operaciones del servicio sean delegadas y desacopladas.

    def get_user_info_for_display(self, card_number: int) -> dict:
        """
        Obtiene y formatea la información de un usuario para la pantalla de éxito.

        :param card_number: Número de tarjeta del usuario.
        :return: Un diccionario con el nombre completo del usuario y su ID. Si el
                 usuario no está registrado, devuelve un mensaje predeterminado.
        """
        user = self._user_repo.find_user_by_card_number(card_number)  # Se consulta el repositorio para centralizar la lógica de acceso a datos.
        if not user:  # Se verifica si el usuario existe para evitar errores y mostrar un mensaje amigable.
            return {'name': 'Usuario aún no registrado', 'id': None}  # Se retorna un valor por defecto para mantener la experiencia de usuario.

        return {'name': user.full_name, 'id': user.id}  # Se formatea la información para que la presentación sea consistente y clara.

    def get_all_lines_for_settings(self) -> list[dict]:
        """
        Obtiene la lista de líneas para mostrar en la página de configuración.

        :return: Una lista de diccionarios que representan las líneas disponibles.
        """
        return self._user_repo.get_all_lines()  # Se delega la obtención de datos al repositorio para mantener la lógica separada y reutilizable.

    def get_user_last_register_type(self, card_number: int) -> Optional[str]:
        """
        Obtiene el tipo del último registro de un empleado.

        :param card_number: Número de tarjeta del usuario.
        :return: El tipo del último registro como cadena, o None si no hay registros.
        """
        return self._user_repo.get_last_register_type(card_number)  # Se consulta el repositorio para encapsular la lógica de negocio y facilitar cambios futuros.

    def register_entry_or_assignment(self, employee_number: int,
                                     side_id: int = 0) -> None:
        """
        Registra la entrada o asignación del operador en la estación/side indicado.

        :param employee_number: Número de empleado asociado al usuario.
        :param side_id: Identificador de la estación o side donde se registra la entrada.
        :raises ValueError: Si el empleado no es encontrado en el repositorio.
        """

        # 2) Delegar la persistencia (el repo debe implementar esta
        # operación)
        self._user_repo.register_entry_or_assignment(user_id=employee_number,
                                                     side_id=side_id)  # Se delega la operación al repositorio para mantener la lógica de persistencia fuera del servicio.

    def get_line_name_by_id(self, line_int: int) -> Optional[str]:
        return self._user_repo.get_line_name_by_id(line_int)  # Se delega la obtención del nombre de línea para centralizar la lógica y facilitar el mantenimiento.