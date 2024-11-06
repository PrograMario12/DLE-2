''' This file contains the User class and functions to simulate a user 
database. '''
from flask_login import UserMixin
from . import database

class User(UserMixin):
    ''' This class represents a user. '''
    def __init__(self, user_id):
        self.id = user_id

    @classmethod
    def get(cls, user_id):
        ''' This function retrieves a user from the database. '''

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
