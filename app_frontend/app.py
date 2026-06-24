"""Punto de entrada de la aplicacion frontend."""

from flask import Flask, render_template

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


@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def error_interno(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)

