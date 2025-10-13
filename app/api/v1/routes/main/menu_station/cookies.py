from __future__ import annotations
from typing import Optional
from flask import request
from app.api.v1.schemas.main import LineCookie

def read_valid_line_cookie() -> Optional[int]:
    """
    Lee y valida la cookie 'line'.

    Returns:
        Optional[int]: El valor entero de la cookie 'line' si es válida, o None si no lo es.

    Detalles:
        - Intenta obtener la cookie 'line' de la solicitud actual.
        - Si la cookie no existe o no es válida, devuelve None.
        - Utiliza el esquema `LineCookie` para validar y convertir el valor de la cookie.
    """
    raw = request.cookies.get("line")  # Obtiene el valor de la cookie 'line'
    if not raw:  # Verifica si la cookie no está presente
        return None
    try:
        # Valida y convierte el valor de la cookie utilizando el esquema `LineCookie`
        return LineCookie.model_validate({"line": raw}).line
    except Exception:
        # Devuelve None si ocurre un error durante la validación
        return None