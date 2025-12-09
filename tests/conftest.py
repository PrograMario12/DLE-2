import pytest
from app.main import create_app
from app.extensions import db
from app.config.settings import Settings

class TestSettings(Settings):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Disable schema for SQLite tests
    DB_SCHEMA = None 

@pytest.fixture(scope='module')
def app():
    # Patch settings to remove schema for SQLite compatibility if possible,
    # or we trust the model definition handles None.
    # The UserModel imports settings at module level. This is hard to patch at runtime for the class definition.
    # Standard fix: Use a real PG database for testing ORM models that use schemas.
    # Or, mock the model.
    # For this simple setup, we'll try to run with standard settings but override URI.
    # CAUTION: If UserModel has 'schema="public"', SQLite will error on API usage unless attached.
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    
    with app.app_context():
        # Setup DB
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@pytest.fixture(scope='module')
def runner(app):
    return app.test_cli_runner()
