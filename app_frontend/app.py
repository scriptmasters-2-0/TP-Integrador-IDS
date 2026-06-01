"""Punto de entrada de la aplicacion frontend."""

import config
from flask import Flask

from routes.admin_routes import admin_bp
from routes.alumno_routes import alumno_bp
from routes.profesor_routes import profesor_bp
from routes.public_routes import public_bp


app = Flask(__name__)
app.register_blueprint(public_bp)
app.register_blueprint(alumno_bp)
app.register_blueprint(profesor_bp)
app.register_blueprint(admin_bp)


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
