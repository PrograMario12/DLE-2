from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class User:
    """Entidad que representa a un empleado."""
    id: int
    name: str
    last_name: str

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.last_name}"

@dataclass(frozen=True)
class StationInfo:
    """DTO para la información de la última estación de un usuario."""
    line_name: Optional[str]
    station_name: Optional[str]