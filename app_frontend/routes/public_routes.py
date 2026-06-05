"""Rutas publicas del frontend."""
from flask import Blueprint, redirect, render_template, request, url_for, session
import requests

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

BACKEND_URL = "http://127.0.0.1:5001"

@public_bp.route("/catalogo", methods=["GET"])
def mostrar_catalogo():
    "Muestra el catalogo completo de articulos con opcion a filtrar por tipo y seccion"
    
    tipo_actual = request.args.get("tipo", "")
    seccion_actual = request.args.get("seccion", "")
    filtros = {}
    if tipo_actual:
        filtros["tipo"] = tipo_actual
    if seccion_actual:
        filtros["seccion"] = seccion_actual
    try:
        response = requests.get(f"{BACKEND_URL}/api/items", params=filtros)
        if response.status_code == 200:
            articulos = response.json()
        else:
            articulos = []
            print(f"Error Backend")
    except Exception:
        pass
    return render_template(
        "public/catalogo.html",
        articulos=articulos,
        tipo_actual=tipo_actual,
        seccion_actual=seccion_actual
    )

@public_bp.route("/faq", methods=["GET"])
def mostrar_faq():
    return render_template("public/faq.html")
