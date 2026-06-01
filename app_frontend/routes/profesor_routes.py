"""Rutas del area de profesores."""

from flask import Blueprint, render_template


profesor_bp = Blueprint("profesor", __name__, url_prefix="/profesor")


@profesor_bp.route("/dashboard")
def dashboard():
    """Renderiza el panel de control del profesor."""
    return render_template("profesor/dashboard.html")
