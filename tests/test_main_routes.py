from flask import Flask
from app.api.v1.routes.main import create_main_bp
from app.main import create_app  # O desde run.py si ahí está la instancia


class StubUserService:
    """
    Clase stub para simular el servicio de usuario.

    Métodos:
        get_user_info_for_display(emp): Devuelve información simulada del usuario para mostrar.
        get_user_last_register_type(emp): Devuelve un tipo de registro simulado para el usuario.
    """
    def get_user_info_for_display(self, emp):
        """
        Obtiene información simulada del usuario para mostrar.

        Args:
            emp (int): Número de empleado.

        Returns:
            dict: Información simulada del usuario con 'id' y 'name'.
        """
        return {"id": emp, "name": "Test"}

    def get_user_last_register_type(self, emp):
        """
        Obtiene un tipo de registro simulado para el usuario.

        Args:
            emp (int): Número de empleado.

        Returns:
            str: Tipo de registro simulado ('Entry').
        """
        return "Entry"

class StubDashService:
    """
    Clase stub para simular el servicio de tableros.

    Métodos:
        get_station_details_for_line(line): Devuelve detalles simulados de la estación para una línea.
    """
    def get_station_details_for_line(self, line):
        """
        Obtiene detalles simulados de la estación para una línea.

        Args:
            line (int): Número de línea.

        Returns:
            dict: Detalles simulados de la estación con clave 'ok'.
        """
        return {"ok": True}

def _app():
    """
    Crea y configura una instancia de la aplicación Flask para pruebas.

    Returns:
        Flask: Aplicación Flask configurada con el blueprint principal.
    """
    app = create_app()
    return app

def test_home_sets_cookie():
    with _app().test_client() as c:
        r = c.get("/")
        assert r.status_code == 200
        assert "employee_number=0" in r.headers.get("Set-Cookie","")

def test_successful_renders_with_cookie():
    """
    Prueba que la ruta '/successful' renderiza correctamente cuando la cookie 'employee_number' está presente.
    """
    with _app().test_client() as c:
        c.set_cookie("employee_number", "7")
        r = c.get("/successful")
        assert r.status_code == 200