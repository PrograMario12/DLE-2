# Import the Flask module
from flask import Flask

# Create a Flask web server from the flask module
app = Flask(__name__)
app.secret_key = 'clave super secreta indescrifrable'

# Use the Flask web server to read the config file
def configure_app():
    app.config.from_pyfile('../config.py')

configure_app()

# Import the routes module
from app import routes