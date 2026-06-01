"""Rutas publicas del frontend."""

from flask import Blueprint, render_template


public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    """Renderiza la pagina de inicio."""
    return render_template("public/index.html")
