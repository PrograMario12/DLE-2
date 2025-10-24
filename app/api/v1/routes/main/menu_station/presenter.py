"""
Presenter para la vista del menú de estaciones.
app/api/v1/routes/main/menu_station/presenter.py
"""

from __future__ import annotations
from typing import Dict, Any, List
import json

# Reglas de presentación (UI): clases CSS y totales

# Constantes que representan clases CSS para el estado de los empleados
EMPLOYEE_NOK = "employee-nook"  # falta personal (amarillo)
EMPLOYEE_OK = "employee-ok"  # justo (verde)
EMPLOYEE_WRN = "employee-warning"  # excede (rojo)

def _side_status_class(cap: int, act: int) -> str:
    """
    Determina la clase CSS para un lado basado en la capacidad y los empleados activos.

    Args:
        cap (int): Capacidad de empleados esperada.
        act (int): Número de empleados activos.

    Returns:
        str: Clase CSS correspondiente al estado del lado.
    """
    if act < cap:
        return EMPLOYEE_NOK
    if act == cap:
        return EMPLOYEE_OK
    return EMPLOYEE_WRN


def build_menu_view_model(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforma los datos crudos en un ViewModel para la plantilla `menu.html`.
        """
        data = dict(raw_data or {})
        print("En presenter.py el data es\n" + json.dumps(data, indent=2, ensure_ascii=False))
        cards = data.get("cards", [])

        total_capacity = total_active = 0

        for card in cards:
            card_cap = card_act = 0
            print(card)

            for side in card.get("sides", []):
                cap = int(side.get("employee_capacity", 0))
                act = int(side.get("employees_working", 0))
                card_cap += cap
                card_act += act

                side.setdefault("class", _side_status_class(cap, act))

            if not card.get("status", True):
                base_class = card.get("class", "")
                card["class"] = f"{base_class} card--{'under' if card_act < card_cap else 'ok' if card_act == card_cap else 'over'}".strip()

            total_capacity += card_cap
            total_active += card_act

        data.update({"cards": cards, "total_capacity": total_capacity, "total_employees": total_active})
        return data