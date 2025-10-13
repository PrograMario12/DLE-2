from __future__ import annotations
from typing import Optional
from pydantic import ValidationError
from app.api.v1.schemas.main import MenuStationForm

def validate_menu_station_form(form_like) -> Optional[MenuStationForm]:
    """Valida el form POST y devuelve el objeto tipado o None si inválido."""
    try:
        return MenuStationForm.model_validate(dict(form_like))
    except (ValidationError, Exception):
        return None