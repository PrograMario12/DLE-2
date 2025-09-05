"""
src/infra/db/database_manager.py
Gestión de la conexión a la base de datos usando Psycopg2.
"""

import psycopg2
from flask import g

class DatabaseManager:
    """Gestiona el ciclo de vida de la conexión a la base de datos."""

    def __init__(self, app):
        self.app = app

    def get_db(self):
        if 'db' not in g:
            g.db = psycopg2.connect(
                host=self.app.config['DB_HOST'],
                port=self.app.config['DB_PORT'],
                dbname=self.app.config['DB_NAME'],
                user=self.app.config['DB_USER'],
                password=self.app.config['DB_PASSWORD']
            )
        return g.db

    def close_db(self, e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

class DBExtension:
    """Simple extensión de Flask para integrar el DatabaseManager."""

    def __init__(self, app=None, db_manager=None):
        if app is not None and db_manager is not None:
            self.init_app(app, db_manager)

    def init_app(self, app, db_manager):
        app.teardown_appcontext(db_manager.close_db)
