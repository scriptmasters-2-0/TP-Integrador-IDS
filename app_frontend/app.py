"""Punto de entrada de la aplicacion frontend."""

from flask import Flask

import config
from routes.admin_routes import admin_bp
from routes.alumno_routes import alumno_bp
from routes.profesor_routes import profesor_bp
from routes.public_routes import public_bp
from routes.biblio_routes import biblio_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.register_blueprint(public_bp)
app.register_blueprint(alumno_bp)
app.register_blueprint(profesor_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(biblio_bp)
app.secret_key = config.SECRET_KEY


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
