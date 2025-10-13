from __future__ import annotations
from typing import Optional
from flask import request
from app.api.v1.schemas.main import LineCookie

def read_valid_line_cookie() -> Optional[int]:
    """Lee y valida la cookie 'line'. Devuelve el entero o None si no es válida."""
    raw = request.cookies.get("line")
    if not raw:
        return None
    try:
        return LineCookie.model_validate({"line": raw}).line
    except Exception:
        return None