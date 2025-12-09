"""
src/infra/db/db.py
Capa de compatibilidad para código legacy que usa psycopg2 directo.
Redirige a la conexión de SQLAlchemy.
DEPRECATED: Refactorizar repositorios a usar SQLAlchemy Models.
"""

from flask import g
from app.extensions import db

def get_db():
    """
    Obtiene una conexión raw (DBAPI) desde el pool de SQLAlchemy.
    Se almacena en 'g' para reutilizarla en la misma request si se llama varias veces.
    """
    if 'db_legacy_conn' not in g:
        # Obtenemos una conexión raw del engine.
        # Esto check-out una conexión del pool.
        g.db_legacy_conn = db.engine.raw_connection()
    return g.db_legacy_conn

def close_db(e=None):
    """
    Cierra la conexión legacy y la devuelve al pool.
    """
    conn = g.pop('db_legacy_conn', None)
    if conn:
        conn.close()

def init_app(app):
    """
    Registra el cierre de la conexión legacy.
    """
    app.teardown_appcontext(close_db)