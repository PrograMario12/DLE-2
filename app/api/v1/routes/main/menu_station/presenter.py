from __future__ import annotations
from typing import Dict, Any, List

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
    elif act == cap:
        return EMPLOYEE_OK
    return EMPLOYEE_WRN


def build_menu_view_model(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforma los datos crudos del servicio en un ViewModel listo para la plantilla `menu.html`.

    Args:
        raw_data (Dict[str, Any]): Datos crudos que contienen información de tarjetas y lados.

    Returns:
        Dict[str, Any]: ViewModel con las siguientes claves:
            - cards (List[Dict]): Lista de tarjetas con clases CSS asignadas.
            - total_capacity (int): Capacidad total esperada de empleados.
            - total_employees (int): Número total de empleados activos.

    Notas:
        - Cada tarjeta puede contener múltiples lados, y cada lado tiene una capacidad y empleados activos.
        - Se asignan clases CSS a cada lado y tarjeta según su estado.
    """
    data = dict(raw_data or {})
    cards: List[dict] = data.get("cards") or []

    total_capacity = 0  # Capacidad total esperada
    total_active = 0  # Total de empleados activos

    for card in cards:
        card_cap = 0  # Capacidad total de la tarjeta
        card_act = 0  # Empleados activos en la tarjeta

        for side in card.get("sides", []):
            cap = int(side.get("employee_capacity") or 0)  # Capacidad del lado
            act = int(side.get("employees_working") or 0)  # Empleados activos en el lado
            card_cap += cap
            card_act += act

            # Asigna una clase CSS al lado si no tiene una
            if not side.get("class"):
                side["class"] = _side_status_class(cap, act)

        # Asigna una clase CSS a la tarjeta si está visible
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

    # Actualiza el ViewModel con los datos procesados
    data["cards"] = cards
    data["total_capacity"] = total_capacity
    data["total_employees"] = total_active
    return data