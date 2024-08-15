from flask import Flask
from routes.main_routes import main_bp
from routes.visualization_routes import visualization_bp
from routes.settings_routes import settings_bp

app = Flask(__name__)

app.register_blueprint(main_bp)
app.register_blueprint(visualization_bp)
app.register_blueprint(settings_bp)

if __name__ == '__main__':
    app.run(debug=True)