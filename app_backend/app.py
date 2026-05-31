"""Punto de entrada de la aplicación Flask del backend."""

import os

from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from flask_login import LoginManager

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)


import config
from database import init_database
from routes.auth_route import auth_bp
from routes.items_route import items_bp
from routes.loans_route import loans_bp
from routes.penalties_route import penalties_bp
from routes.salud_route import blueprint_salud
from routes.qr_route import qr_bp
from routes.users_routes import users_bp
from routes.reportes_route import blueprint_reportes

init_database()

app.register_blueprint(auth_bp)
app.register_blueprint(items_bp)
app.register_blueprint(loans_bp)
app.register_blueprint(penalties_bp)
app.register_blueprint(blueprint_salud)
app.register_blueprint(users_bp)
app.register_blueprint(qr_bp)
app.register_blueprint(blueprint_reportes)

HERE = os.path.dirname(__file__)


@app.route("/swagger.yaml")
def swagger_spec():
    """Sirve el archivo de especificación OpenAPI.

    Returns:
        Response: El archivo swagger.yaml desde el directorio actual.

    """
    return send_from_directory(HERE, "swagger.yaml")


SWAGGER_URL = "/api/docs"
API_URL = "/swagger.yaml"
swaggerui_bp = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={"app_name": "TP Integrador API"})
app.register_blueprint(swaggerui_bp, url_prefix=SWAGGER_URL)


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
