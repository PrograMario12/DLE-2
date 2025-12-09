"""
src/infra/db/user_repository_sql.py
Implementación del repositorio de usuarios usando SQLAlchemy.
"""

from app.extensions import db
from app.domain.entities.user import User
from app.domain.repositories.IUserRepository import IUserRepository
from app.infra.db.models import UserModel
from typing import Optional

class UserRepositorySQL(IUserRepository):
    """Implementación del repositorio de usuarios con SQLAlchemy."""

    def __init__(self, schema: str):
        # Schema is handled by the Model definition, but we keep the signature valid.
        self.schema = schema

    def find_user_by_card_number(self, card_number: int) -> Optional[User]:
        # ORM Query
        # We cast card_number to string if the DB column is string
        model = db.session.query(UserModel).filter(UserModel.numero_tarjeta == str(card_number)).first()
        
        if not model:
            return None

        return model.to_entity()

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Encuentra un usuario por su id_empleado."""
        model = db.session.get(UserModel, user_id)
        
        if not model:
            return None

        return model.to_entity()
