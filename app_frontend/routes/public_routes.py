"""Rutas publicas del frontend."""

from flask import Blueprint, redirect, render_template, request, url_for


public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    """Renderiza la pagina de inicio."""
    return render_template("public/index.html")


@public_bp.route("/logout", methods=["GET"])
def logout():
    """Cierra la sesión del usuario y redirige a la página de inicio."""
    # Limpiamos la sesión activa
    # session.clear()
    # Renderizamos la pantalla de salida
    return render_template("public/logout.html")


@public_bp.route("/registro", methods=["GET", "POST"])
def registro():
    """Renderiza la página de registro y maneja el proceso de registro de nuevos usuarios."""
    if request.method == "POST":
        # 1. Capturar datos del form
        # 2. Llamar a la API de backend para crear el usuario con rol 'alumno'
        # 3. Redirigir a /login
        return redirect(url_for("public.login"))

    return render_template("public/registro.html")


@public_bp.route("/normas", methods=["GET"])
def normas():
    # En una implementación real, podrías obtener las normas desde la DB
    # normas = requests.get(f"{BACKEND_URL}/normativa").json()
    return render_template("public/normas.html")
