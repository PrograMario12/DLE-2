from app.domain.repositories.IUserRepository import IUserRepository

class StationService:
    """
    Servicio con la lógica de negocio para las estaciones.
    Depende de la abstracción IUserRepository (DIP).
    """

    def __init__(self, user_repo: IUserRepository):
        """
        Inicializa el servicio de estaciones con un repositorio de usuarios.

        :param user_repo: Implementación de la interfaz IUserRepository para
                          interactuar con los datos de los usuarios.
        """
        self._user_repo = user_repo

    def get_user_status_for_display(self, card_number: int):
        """
        Prepara los datos del usuario para la pantalla de éxito.

        Este método obtiene la información del usuario asociada al número de tarjeta
        proporcionado y determina si el último registro fue una entrada o una salida.
        Luego, prepara un diccionario con los datos necesarios para mostrar en la
        pantalla, incluyendo el nombre del usuario, el tipo de registro, el color
        asociado y la información de la estación.

        :param card_number: Número de tarjeta del usuario.
        :return: Diccionario con los datos del usuario para la pantalla de éxito.
                 Si el usuario no es encontrado, retorna un diccionario con un error.
        """
        user = self._user_repo.find_user_by_card_number(card_number)
        if not user:
            return {"error": "User not found"}

        last_register = self._user_repo.get_last_register_type(card_number)

        if last_register == 'Exit':
            return {
                "user": user.full_name, "type": "Entrada",
                "color": "employee-ok", "image": f"{user.id}.png",
            }

        return {
            "user": user.full_name, "type": "Salida",
            "color": "employee-warning", "image": f"{user.id}.png",
        }
