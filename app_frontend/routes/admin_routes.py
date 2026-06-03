"""Rutas del area de administracion."""

from flask import Blueprint, render_template


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/prestamos/id")
def prestamo_detalle():
    """Renderiza la vista de detalle de prestamo para administradores."""
    return render_template("admin/prestamo_detalle.html")


@admin_bp.route("/articulos")
def listar_articulos():
    """Renderiza la vista de listado de artículos para administradores."""
    # Aquí realizarías la petición al backend para obtener los artículos
    # articulos = requests.get(f"{BACKEND_URL}/items").json()
    return render_template("admin/articulos.html")


@admin_bp.route("/articulos/nuevo")
def crear_articulo():
    """Renderiza la vista de creación de nuevo artículo para administradores."""
    return render_template("admin/articulos_form.html")


@admin_bp.route("/dashboard")
def dashboard():
    """Renderiza la vista del dashboard para administradores."""
    # En una implementación real:
    # metrics = requests.get(f"{BACKEND_URL}/reports?type=dashboard").json()
    return render_template("admin/dashboard.html")
