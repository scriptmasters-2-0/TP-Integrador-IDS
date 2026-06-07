"""Rutas publicas del frontend."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from http_codes_and_messages import HTTP_UNAUTHORIZED
from services import auth_service, normativas_service
from services.api_client import get_json, post_json
from services.items_service import obtener_items

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    """Renderiza la pagina de inicio."""
    return render_template("public/index.html")


@public_bp.route("/logup", methods=["GET"])
def logup():
    """Renderiza la página de registro de nuevos usuarios."""
    if session.get("token"):
        role = session.get("role", "alumno")
        if role in ("admin", "bibliotecario"):
            return redirect(url_for("admin.dashboard"))
        if role in ("profesor", "docente"):
            return redirect(url_for("profesor.mis_reservas"))
        return redirect(url_for("alumno.perfil"))

    return render_template("public/registro.html")


@public_bp.route("/logup", methods=["POST"])
def logup_submit():
    """Procesa logup contra backend."""
    username = (request.form.get("email") or "").strip()
    email = (request.form.get("email") or "").strip()
    carrera = request.form.get("carrera") or ""
    password = request.form.get("password") or ""

    respuesta = auth_service.crear_usuario(
        {"nombre": username, "mail": email, "carrera": carrera, "password": password},
    )

    if not respuesta:
        return (
            render_template(
                "public/registro.html",
                hasError=True,
                errorMessage="No se pudo crear el usuario. Intente nuevamente.",
            ),
            HTTP_UNAUTHORIZED,
        )

    return redirect(url_for("public.login"))


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

    return render_template("public/login.html")


@public_bp.route("/login", methods=["POST"])
def login_submit():
    """Procesa login contra backend y guarda sesión local."""
    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""

    payload, error, status_code = post_json(
        "/auth/login", {"email": email, "password": password}
    )

    if error:
        print(error)
        return (
            render_template(
                "public/login.html",
                hasError=True,
                errorMessage=f"No se pudo iniciar sesión ({status_code}): {error}",
            ),
            HTTP_UNAUTHORIZED,
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
        return redirect(url_for("public.login"))
    return render_template("public/registro.html")


@public_bp.route("/normas", methods=["GET"])
def normas():
    normativas = normativas_service.obtener_normativas()
    return render_template("public/normas.html", normativas=normativas)


@public_bp.route("/catalogo", methods=["GET"])
def mostrar_catalogo():
    """Muestra el catálogo completo de artículos con filtros opcionales."""
    tipo_actual = request.args.get("tipo", "")
    seccion_actual = request.args.get("seccion", "")
    filtros = {}
    if tipo_actual:
        filtros["tipo"] = tipo_actual
    if seccion_actual:
        filtros["seccion"] = seccion_actual

    articulos = obtener_items(filtros)

    return render_template(
        "public/catalogo.html",
        articulos=articulos,
        tipo_actual=tipo_actual,
        seccion_actual=seccion_actual,
    )


@public_bp.route("/faq", methods=["GET"])
def mostrar_faq():
    return render_template("public/faq.html")


@public_bp.route("/articulos/<int:item_id>")
def get_article_details(item_id):
    """Muestra el detalle público de un artículo."""
    articulo, fetch_error = get_json(f"/api/items/{item_id}")

    return render_template(
        "public/article_details.html", articulo=articulo, fetch_error=fetch_error
    )
