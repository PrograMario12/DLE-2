import psycopg2
from flask import current_app, g

def get_db():
    """
    Abre una nueva conexión a la base de datos si no existe una para
    el contexto de la petición actual.
    """
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=current_app.config['DB_HOST'],
            port=current_app.config['DB_PORT'],
            dbname=current_app.config['DB_NAME'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD']
        )
    return g.db

def close_db(e=None):
    """
    Cierra la conexión a la base de datos si existe en el contexto
    de la petición.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Registra las funciones de la base de datos con la aplicación Flask."""
    app.teardown_appcontext(close_db)