# tests/mocks/MockActiveStaffRepository.py
from app.domain.repositories.IActiveStaffRepository import IActiveStaffRepository
from app.domain.entities.user import User

class MockActiveStaffRepository(IActiveStaffRepository):
    def get_all(self):
        # Retorna una lista simulada de usuarios
        return [
            User(id=1, name="Empleado 1", last_name="Apellido 1",
                 numero_tarjeta=12345),
            User(id=2, name="Empleado 2", last_name="Apellido 2", numero_tarjeta=67890),
            User(id=3, name="Empleado 3", last_name="Apellido 3", numero_tarjeta=1234567890),
        ]