from flask_login import LoginManager
from .infra.db.database_manager import DBExtension

# Instancias de las extensiones que se inicializarán en la fábrica
db = DBExtension()
login_manager = LoginManager()