import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuraciones de la aplicación cargadas desde el entorno."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'default-super-secret-key')

    # Configuración de la base de datos (Raw params)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_SCHEMA = os.getenv('DB_SCHEMA', 'public')

    # SQLAlchemy
    # Construct URI. For async: postgresql+asyncpg://...
    # For now we use sync as default for refactor step 1, but prepare for async.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Async URI example
    SQLALCHEMY_ASYNC_DATABASE_URI = os.getenv(
        'ASYNC_DATABASE_URL',
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Configuración del servidor
    HOST = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_RUN_PORT', 5000))
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1')
    TESTING = False

settings = Settings()