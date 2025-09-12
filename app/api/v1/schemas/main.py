"""Esquemas Pydantic para cookies y formularios de main."""
from pydantic import BaseModel, Field

class EmployeeCookie(BaseModel):
    """
    Esquema para validar la cookie 'employee_number'.

    Atributos:
        employee_number (int): Número de empleado. Debe ser un entero mayor o igual a 0.
    """
    employee_number: int = Field(default=0, ge=0)

class LineCookie(BaseModel):
    """
    Esquema para validar la cookie 'line'.

    Atributos:
        line (int): Número de línea. Debe ser un entero mayor o igual a 1.
    """
    line: int = Field(ge=1)

class MenuStationForm(BaseModel):
    """
    Esquema para validar los datos del formulario de menú de estación.

    Atributos:
        employee_number (int): Número de empleado. Debe ser un entero mayor o igual a 1.
    """
    employee_number: int = Field(ge=1)