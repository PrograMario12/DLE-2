"""
Application Factory and Entry Point for Flask.

Use this script to create and configure the Flask application
instance.
It can also be run directly to start the development server.
"""

import os
from flask import Flask
from flask_login import LoginManager

from .user_model import User
from . import settings
from . import main
from . import dashboards

def create_app():
    ''' This function creates the Flask application. '''
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_name):
        ''' This function loads a user. '''
        return User.get(user_name)

    configure_app(app)
    register_blueprints(app)

    return app

def configure_app(app):
    ''' This function configures the Flask application. '''
    try:
        app.config.from_pyfile('../config.py')
    except FileNotFoundError:
        print("Configuration file not found. Using default settings.")

def register_blueprints(app):
    ''' This function registers the blueprints. '''
    app.register_blueprint(main.main_bp)
    app.register_blueprint(dashboards.dashboards_bp)
    app.register_blueprint(settings.settings_bp)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
