''' This is the main file that runs the Flask web server. It imports 
the routes module and runs the Flask web server. '''

from flask import Flask
from flask_login import LoginManager

from app import settings
from . import main
from . import dashboards

app = Flask(__name__)
app.secret_key = 'Top secret key unbreakable code'

login_manager = LoginManager()
login_manager.init_app(app)

def configure_app():
    ''' This function configures the Flask application. '''
    app.config.from_pyfile('../config.py')

configure_app()

app.register_blueprint(main.main_bp)

app.register_blueprint(dashboards.dashboards_bp)

if __name__ == '__main__':
    app.run(debug=True)
