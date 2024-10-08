'''A simple in-memory database'''

import psycopg2
import config as Config

class Database:
    '''A simple in-memory database'''
    def __init__(self):
        self.connection = None

    def connect(self):
        '''Connect to the database'''
        try:
            self.connection = psycopg2.connect(
                host=Config.DATABASE_HOST,
                user=Config.DATABASE_USER,
                database=Config.DATABASE_NAME,
                password=Config.DATABASE_PASSWORD,
                port=Config.DATABASE_PORT
            )
            print('Connected to the database')
        except psycopg2.Error as error:
            print(f'Error: {error}')
            self.connection = None

    def disconnect(self):
        '''Disconnect from the database'''
        if self.connection:
            self.connection.close()
            print('Disconnected from the database')

    def execute_query(self, query):
        '''Execute a query in the database'''
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SET search_path TO {Config.SCHEMA_NAME}")
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        return None

    def insert_query(self, query):
        '''Insert a query in the database'''
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SET search_path TO {Config.SCHEMA_NAME}")
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return True
        return False