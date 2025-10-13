from __future__ import annotations
from typing import Dict, Any, List

# Reglas de presentación (UI): clases CSS y totales

EMPLOYEE_NOK = "employee-nook"  # falta personal (amarillo)
EMPLOYEE_OK = "employee-ok"  # justo (verde)
EMPLOYEE_WRN = "employee-warning"  # excede (rojo)

def _side_status_class(cap: int, act: int) -> str:
    if act < cap:
        return EMPLOYEE_NOK
    elif act == cap:
        return EMPLOYEE_OK
    return EMPLOYEE_WRN


def build_menu_view_model(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transforma `raw_data` del servicio en un ViewModel listo para `menu.html`.
    Espera llaves: { "cards": [ {"status": bool, "sides": [{"employee_capacity": int, "employees_working": int, ...}], ... } ] }
    Devuelve:
    - cards: con clases CSS por side y por card
    - total_capacity (Fuera de estándar) y total_employees (Real)
    """
    data = dict(raw_data or {})
    cards: List[dict] = data.get("cards") or []

    total_capacity = 0
    total_active = 0

    for card in cards:
        card_cap = 0
        card_act = 0

        for side in card.get("sides", []):
            cap = int(side.get("employee_capacity") or 0)
            act = int(side.get("employees_working") or 0)
            card_cap += cap
            card_act += act

            if not side.get("class"):
                side["class"] = _side_status_class(cap, act)

        # Fondo de la tarjeta grande, solo si está visible
        if not card.get("status", True):
            base = (card.get("class") or "")
            if card_act < card_cap:
                card["class"] = f"{base} card--under".strip()
            elif card_act == card_cap:
                card["class"] = f"{base} card--ok".strip()
            else:
                card["class"] = f"{base} card--over".strip()

            total_capacity += card_cap
            total_active += card_act

    data["cards"] = cards
    data["total_capacity"] = total_capacity
    data["total_employees"] = total_active
    return data
