"""Rutas del area de administracion."""

from flask import Blueprint, render_template


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/prestamos/id")
def prestamo_detalle():
    """Renderiza la vista de detalle de prestamo para administradores."""
    return render_template("admin/prestamo_detalle.html")
