"""
user_model.py
This module defines the User model for the application, integrating
with Flask-Login for user session management.
It provides an in-memory simulation of a user database for quick
access and testing, as well as methods to interact
with a persistent database to retrieve user information. The module
includes:
- The User class, which represents a user and provides methods to add
and retrieve users from the in-memory store.
- The get_name_user function, which queries the persistent database to
retrieve a user's full name based on their ID.
Intended for use in authentication and user management workflows
within the application.
"""
from flask_login import UserMixin
from . import database

class User(UserMixin):
    ''' This class represents a user. '''
    _users_db = {}  # Simulación de "base de datos" en memoria

    def __init__(self, user_id):
        self.id = user_id

    @classmethod
    def add_user_to_cache(cls, user):
        '''Agrega un usuario a la "base de datos" en memoria.'''
        if user and user.id:
            cls._users_db[user.id] = user

    @classmethod
    def get(cls, user_id):
        ''' This function retrieves a user from the database o de la memoria. '''
        # Primero busca en la "DB" simulada
        if user_id in cls._users_db:
            return cls._users_db[user_id]

        user_name = get_name_user(user_id)
        if user_name:
            print(f'User {user_id} retrieved.')
            return cls(user_id)
        return None

def get_name_user( user_id):
    ''' This function retrieves the name of a user from the 
    database. '''
    db = database.Database()

    query = f"""
        SELECT nombre_empleado || ' ' || apellidos_empleado
        FROM table_empleados_tarjeta
        WHERE numero_tarjeta = {user_id}
    """
    db.connect()
    results = db.execute_query(query)
    db.disconnect()

    if not results:
        return None
    return results[0][0]
