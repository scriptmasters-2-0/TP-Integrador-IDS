"""Rutas del area de alumnos."""

from flask import Blueprint, render_template


alumno_bp = Blueprint("alumno", __name__, url_prefix="/alumno")


@alumno_bp.route("/perfil")
def perfil():
    """Renderiza la pagina de perfil del alumno."""
    return render_template("alumno/perfil.html")


@alumno_bp.route("/historial")
def historial():
    """Renderiza el historial de prestamos del alumno."""
    return render_template("alumno/historial.html")


@alumno_bp.route("/prestamos/id/comprobante")
def comprobante():
    """Renderiza el comprobante de un prestamo especifico para el alumno."""
    return render_template("alumno/comprobante.html")
