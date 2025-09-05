import os
from dotenv import load_dotenv

load_dotenv()  # Carga variables de un archivo .env si existe


class Settings:
    """Configuraciones de la aplicación cargadas desde el entorno."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'default-super-secret-key')

    # Configuración de la base de datos
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    # Configuración del servidor
    HOST = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_RUN_PORT', 5000))
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1')


settings = Settings()