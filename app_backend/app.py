from database import init_database
from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from routes.ping import ping_bp
from routes.usuarios_route import usuarios_bp
from routes.auth_route import auth_bp
from routes.penalties_route import penalties_bp
import config
import os

app = Flask(__name__)

init_database()

app.register_blueprint(ping_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(penalties_bp)

HERE = os.path.dirname(__file__)


@app.route("/swagger.yaml")
def swagger_spec():
    return send_from_directory(HERE, "swagger.yaml")


SWAGGER_URL = "/api/docs"
API_URL = "/swagger.yaml"
swaggerui_bp = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "TP Integrador API"}
)
app.register_blueprint(swaggerui_bp, url_prefix=SWAGGER_URL)

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
