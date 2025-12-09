from sqlalchemy import Column, Integer, String
from app.extensions import db
from app.config.settings import settings

class UserModel(db.Model):
    __tablename__ = 'table_empleados_tarjeta'
    __table_args__ = {'schema': settings.DB_SCHEMA}
    
    id_empleado = Column(Integer, primary_key=True)
    nombre_empleado = Column(String)
    apellidos_empleado = Column(String)
    numero_tarjeta = Column(String) # Handled as String for flexibility
    
    def to_entity(self):
        from app.domain.entities.user import User
        # Ensure strict typing for Entity
        try:
            target_id = int(self.numero_tarjeta) if self.numero_tarjeta else 0
        except ValueError:
            target_id = 0
            
        return User(
            id=self.id_empleado,
            name=self.nombre_empleado,
            last_name=self.apellidos_empleado,
            numero_tarjeta=target_id
        )
