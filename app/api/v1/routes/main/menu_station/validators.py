from __future__ import annotations
from typing import Optional
from pydantic import ValidationError
from app.api.v1.schemas.main import MenuStationForm

def validate_menu_station_form(form_like) -> Optional[MenuStationForm]:
    """
    Valida un formulario POST relacionado con el menú de estación.

    Args:
        form_like: Objeto similar a un diccionario que contiene los datos del formulario.

    Returns:
        Optional[MenuStationForm]: Una instancia validada de `MenuStationForm` si los datos son válidos,
        o `None` si la validación falla.

    Notas:
        - Utiliza el método `model_validate` de Pydantic para validar y convertir los datos.
        - Si ocurre un error de validación (`ValidationError`) o cualquier otra excepción, devuelve `None`.
    """
    try:
        return MenuStationForm.model_validate(dict(form_like))
    except (ValidationError, Exception):
        return None