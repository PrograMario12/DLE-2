from app.domain.repositories.IUserRepository import IUserRepository
from app.domain.repositories.IRegisterRepository import IRegisterRepository

class StationService:
    """
    Servicio con la lógica de negocio para las estaciones.
    Depende de las abstracciones IUserRepository e IRegisterRepository (DIP).
    """

    def __init__(self, user_repo: IUserRepository, register_repo: IRegisterRepository):
        """
        Inicializa el servicio de estaciones con los repositorios necesarios.

        :param user_repo: Implementación de IUserRepository.
        :param register_repo: Implementación de IRegisterRepository.
        """
        self._user_repo = user_repo
        self._register_repo = register_repo

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

        last_register = self._register_repo.get_last_register_type(card_number)
        station_info = self._register_repo.get_last_station_for_user(card_number)

        line_name = station_info.get("line_name") if station_info else None
        station_name = station_info.get("station_name") if station_info else None

        if last_register == 'Exit':
            return {
                "user": user.full_name, "type": "Entrada",
                "color": "employee-ok", "image": f"{user.id}.png",
                "line_name": line_name, "station_name": station_name
            }

        return {
            "user": user.full_name, "type": "Salida",
            "color": "employee-warning", "image": f"{user.id}.png",
            "line_name": line_name, "station_name": station_name
        }
