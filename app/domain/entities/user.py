from dataclasses import dataclass
from typing import Optional
from flask_login import UserMixin # <-- 1. IMPORTA UserMixin

@dataclass(frozen=True)
class User(UserMixin): # <-- 2. HEREDA de UserMixin
    """Entidad de negocio que representa a un empleado."""
    id: int
    name: str
    last_name: str
    numero_tarjeta: int

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.last_name}"

@dataclass(frozen=True)
class StationInfo:
    """DTO para la información de la última estación de un usuario."""
    line_name: Optional[str]
    station_name: Optional[str]