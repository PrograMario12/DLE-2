# Import the Flask module
from flask import Flask

# Create a Flask web server from the flask module
app = Flask(__name__)
app.secret_key = 'Top secret key unbreakable code' 

# Use the Flask web server to read the config file
def configure_app():
    app.config.from_pyfile('../config.py')

configure_app()

from . import main
app.register_blueprint(main.main_bp)

from . import dashboards
app.register_blueprint(dashboards.dashboards_bp)

# Import the routes module
from app import routes