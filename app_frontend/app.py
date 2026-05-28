"""Módulo principal de la aplicación frontend.

Configura e inicializa la aplicación Flask del frontend y define
la ruta principal para servir la página de inicio.
"""

import config
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    """Renderiza la página de inicio del frontend.

    Returns:
        str: Contenido HTML de la plantilla 'index.html'.
    """
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
