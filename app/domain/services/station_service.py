from datetime import datetime
from app.domain.repositories.user_repository import IUserRepository


class StationService:
    """
    Servicio con la lógica de negocio para las estaciones.
    Depende de la abstracción IUserRepository (DIP).
    """

    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo

    def get_user_status_for_display(self, card_number: int):
        """Prepara los datos para la pantalla de éxito."""
        user = self._user_repo.find_by_card_number(card_number)
        if not user:
            # Manejar el caso de usuario no encontrado apropiadamente
            return {"error": "User not found"}

        last_register = self._user_repo.get_last_register_type(card_number)

        if last_register == 'Entry':
            # Lógica para registrar entrada (simplificada)
            # self._user_repo.register_entry(...)
            station_info = self._user_repo.get_last_station_info(user.id)
            return {
                "user": user.full_name, "type": "Entrada",
                "color": "employee-ok", "image": f"{user.id}.png",
                **station_info.__dict__
            }

        # Lógica para registrar salida (simplificada)
        # self._user_repo.register_exit(...)
        station_info = self._user_repo.get_last_station_info(user.id)
        return {
            "user": user.full_name, "type": "Salida",
            "color": "employee-warning", "image": f"{user.id}.png",
            **station_info.__dict__
        }