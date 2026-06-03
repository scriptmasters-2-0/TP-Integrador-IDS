"""Rutas publicas del frontend."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from services.api_client import post_json


public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    """Renderiza la pagina de inicio."""
    return render_template("public/index.html")


@public_bp.route("/login", methods=["GET"])
def login():
    """Renderiza la página de inicio de sesión."""
    if session.get("token"):
        role = session.get("role", "alumno")
        if role in ("admin", "bibliotecario"):
            return redirect(url_for("admin.dashboard"))
        if role in ("profesor", "docente"):
            return redirect(url_for("profesor.mis_reservas"))
        return redirect(url_for("alumno.perfil"))

    return render_template("public/login.html", login_error=None)


@public_bp.route("/login", methods=["POST"])
def login_submit():
    """Procesa login contra backend y guarda sesión local."""
    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""

    payload, error, status_code = post_json(
        "/api/auth/login", {"email": email, "password": password}
    )

    if error:
        return (
            render_template(
                "public/login.html",
                login_error=f"No se pudo iniciar sesión ({status_code}): {error}",
            ),
            401,
        )

    role = (payload or {}).get("role", "alumno")
    session["token"] = (payload or {}).get("token")
    session["role"] = role
    session["user"] = (payload or {}).get("user", {})

    if role in ("admin", "bibliotecario"):
        return redirect(url_for("admin.dashboard"))
    if role in ("profesor", "docente"):
        return redirect(url_for("profesor.mis_reservas"))
    return redirect(url_for("alumno.perfil"))


@public_bp.route("/logout", methods=["GET"])
def logout():
    """Cierra la sesión del usuario y redirige a la página de inicio."""
    session.clear()
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
