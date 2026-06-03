"""Rutas del area de profesores."""

from flask import Blueprint, redirect, render_template


profesor_bp = Blueprint("profesor", __name__, url_prefix="/profesor")


@profesor_bp.route("/dashboard")
def dashboard():
    """Renderiza el panel de control del profesor."""
    return render_template("profesor/dashboard.html")


@profesor_bp.route("/nueva", methods=["GET"])
def nueva_reserva():
    """Renderiza el formulario para crear una nueva reserva."""
    # Aquí podrías obtener la lista de artículos disponibles
    # articulos = requests.get(f"{BACKEND_URL}/items?available=true").json()
    return render_template("profesor/nueva_reserva.html")


@profesor_bp.route("/guardar", methods=["POST"])
def guardar_reserva():
    """Lógica para guardar la nueva reserva."""
    # Lógica para enviar a /loans (POST) según ARCHITECTURE.md
    # data = request.form
    # response = requests.post(f"{BACKEND_URL}/loans", json=data)
    return redirect("/dashboard")
