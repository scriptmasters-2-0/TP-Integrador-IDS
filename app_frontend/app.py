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

@app.route("/alumno/perfil")
def alumno_perfil():
    """Renderiza la página de perfil del alumno.

    Returns:
        str: Contenido HTML de la plantilla 'alumno_perfil.html'.
    """
    return render_template("alumno_perfil.html")

@app.route("/alumno/historial")
def alumno_historial():
    """Renderiza el historial de préstamos del alumno.

    Returns:
        str: Contenido HTML de la plantilla 'alumno_historial.html'.
    """
    return render_template("alumno_historial.html")

@app.route("/alumno/prestamos/id/comprobante")
def comprobante_alumno():
    """Renderiza el comprobante de un préstamo específico para el alumno.

    Returns:
        str: Contenido HTML de la plantilla 'alumno_comprobante.html'.
    """
    return render_template("alumno_comprobante.html")

@app.route("/profesor/dashboard")
def dashboard_profesor():
    """Renderiza el panel de control del profesor.

    Returns:
        str: Contenido HTML de la plantilla 'profesor_dashboard.html'.
    """
    return render_template("profesor_dashboard.html")

@app.route("/admin/prestamos/id")
def prestamos_admin():
    """Renderiza la vista de detalle de préstamo para administradores.

    Returns:
        str: Contenido HTML de la plantilla 'admin_prestamo_detalle.html'.
    """
    return render_template("admin_prestamo_detalle.html")


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
