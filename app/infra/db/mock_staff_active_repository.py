# tests/mocks/MockActiveStaffRepository.py
from app.domain.repositories.IActiveStaffRepository import IActiveStaffRepository
from app.domain.entities.user import User

class MockActiveStaffRepository(IActiveStaffRepository):
    def get_all(self):
        # Retorna una lista simulada de usuarios
        return [
            User(id=1, name="Empleado 1", last_name="Apellido 1"),
            User(id=2, name="Empleado 2", last_name="Apellido 2"),
            User(id=3, name="Empleado 3", last_name="Apellido 3"),
        ]