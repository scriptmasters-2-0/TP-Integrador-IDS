"""Punto de entrada de la aplicación Flask del backend."""

import os

from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint

import config
from database import init_database
from routes.auth_route import auth_bp
from routes.articulos_route import articulos_bp
from routes.reservas_route import reservas_bp
from routes.normativas_route import normativas_bp
from routes.penalizaciones_route import penalizaciones_bp
from routes.qr_route import qr_bp
from routes.reportes_route import reportes_bp
from routes.salud_route import salud_bp
from routes.usuarios_routes import usuarios_bp

app = Flask(__name__)


app.register_blueprint(auth_bp)
app.register_blueprint(articulos_bp)
app.register_blueprint(reservas_bp)
app.register_blueprint(penalizaciones_bp)
app.register_blueprint(salud_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(qr_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(normativas_bp)

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
swaggerui_bp = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "TP Integrador API"}
)
app.register_blueprint(swaggerui_bp, url_prefix=SWAGGER_URL)


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
