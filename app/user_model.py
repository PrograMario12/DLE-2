''' This file contains the User class and functions to simulate a user 
database. '''
from flask_login import UserMixin
from . import functions

class User(UserMixin):
    ''' This class represents a user. '''
    def __init__(self, user_id):
        self.id = user_id

    @classmethod
    def get(cls, user_id):
        ''' This function retrieves a user from the database. '''

        user_name = functions.get_user(user_id)

        if user_name:
            return cls(user_id)
        return None
