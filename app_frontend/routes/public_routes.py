"""Rutas publicas del frontend."""

import logging

from flask import Blueprint, redirect, render_template, request, session, url_for

from http_codes_and_messages import HTTP_FORBIDDEN, HTTP_UNAUTHORIZED
from servicios import auth_servicio, normativas_servicio
from servicios.api_client import get_json, post_json
from servicios.articulos_servicio import obtener_articulos_paginados
from servicios.paginacion_servicio import adaptar_pagination_hateoas, calcular_offset, DEFAULT_API_LIMIT
from servicios.fechas_servicio import formatear_fecha_argentina

public_bp = Blueprint("public", __name__)
logger = logging.getLogger(__name__)


@public_bp.route("/")
def home():
    """Renderiza la pagina de inicio."""
    token = session.get("token")
    if token:
        rol = session.get("rol", "alumno")
        if rol in ("admin", "bibliotecario"):
            return redirect(url_for("admin.dashboard"))
        if rol == "profesor":
            return redirect(url_for("profesor.mis_reservas"))
        return redirect(url_for("alumno.dashboard"))
    return render_template("public/index.html")


@public_bp.route("/logup", methods=["GET"])
def logup():
    """Renderiza la página de registro de nuevos usuarios."""
    if session.get("token"):
        rol = session.get("rol", "alumno")
        if rol in ("admin", "bibliotecario"):
            return redirect(url_for("admin.dashboard"))
        if rol == "profesor":
            return redirect(url_for("profesor.mis_reservas"))
        return redirect(url_for("alumno.dashboard"))

    return render_template("public/registro.html")


@public_bp.route("/logup", methods=["POST"])
def logup_submit():
    """Procesa logup contra backend."""
    nombre = (request.form.get("nombre") or "").strip()
    email = (request.form.get("email") or "").strip()
    carrera = request.form.get("carrera") or ""
    contrasenia = request.form.get("contrasenia") or ""

    respuesta = auth_servicio.crear_usuario(
        {"nombre": nombre, "email": email, "carrera": carrera, "contrasenia": contrasenia},
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
        rol = session.get("rol", "alumno")
        if rol in ("admin", "bibliotecario"):
            return redirect(url_for("admin.dashboard"))
        if rol == "profesor":
            return redirect(url_for("profesor.dashboard"))
        return redirect(url_for("alumno.dashboard"))

    articulo_id = request.args.get("articulo_id", "")
    return render_template("public/login.html", articulo_id=articulo_id)


@public_bp.route("/login", methods=["POST"])
def login_submit():
    """Procesa login contra backend y guarda sesión local."""
    email = (request.form.get("email") or "").strip()
    contrasenia = request.form.get("contrasenia") or ""

    payload, error, status_code = auth_servicio.autenticar_usuario(
        {"email": email, "contrasenia": contrasenia}
    )

    if error:
        if status_code == HTTP_FORBIDDEN and (payload or {}).get("detail") == "inactive_user":
            return (
                render_template(
                    "public/login.html",
                    hasError=True,
                    errorMessage="Tu cuenta está inactiva o suspendida. Contacta al administrador.",
                ),
                HTTP_FORBIDDEN,
            )

        logger.warning("Error de login: %s", error)
        return (
            render_template(
                "public/login.html",
                hasError=True,
                errorMessage=f"No se pudo iniciar sesión ({status_code}): {error}",
            ),
            HTTP_UNAUTHORIZED,
        )

    rol = (payload or {}).get("rol", "alumno")
    usuario_data = (payload or {}).get("usuario", {})

    session["token"] = (payload or {}).get("token")
    session["rol"] = rol
    session["usuario"] = usuario_data

    articulo_id = request.form.get("articulo_id", "").strip()

    if articulo_id:
        if rol == "profesor":
            return redirect(url_for("profesor.nueva_reserva", articulo_id=articulo_id))
        if rol == "alumno":
            return redirect(url_for("alumno.nueva_reserva", articulo_id=articulo_id))
    
    if rol in ("admin", "bibliotecario"):
        return redirect(url_for("admin.dashboard"))
    if rol == "profesor":
        return redirect(url_for("profesor.dashboard"))
    return redirect(url_for("alumno.dashboard"))


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
    """Descripción: función normas con paginación."""
    page = request.args.get("page", 1, type=int) or 1
    offset = calcular_offset(page, DEFAULT_API_LIMIT)

    payload_paginado, fetch_error = normativas_servicio.obtener_normativas_paginadas(
        params={"limit": DEFAULT_API_LIMIT, "offset": offset}
    )
    normativas_raw = payload_paginado.get("data", []) if not fetch_error else []

    normativas = [
        {
            **normativa,
            "fecha": formatear_fecha_argentina(normativa.get("fecha")),
        }
        for normativa in normativas_raw
    ]
    pagination = adaptar_pagination_hateoas(payload_paginado, pagina=page)

    return render_template(
        "public/normas.html",
        normativas=normativas,
        pagination=pagination,
    )


@public_bp.route("/catalogo", methods=["GET"])
def mostrar_catalogo():
    """Muestra el catálogo completo de artículos paginado con filtros opcionales."""
    opciones = articulos_servicio.obtener_opciones_articulo()
    tipos = opciones.get("tipos", [])
    secciones = opciones.get("secciones", [])
    tipos_validos = {opcion.get("valor") for opcion in tipos}
    secciones_validas = {opcion.get("valor") for opcion in secciones}

    tipo_actual = request.args.get("tipo", "")
    seccion_actual = request.args.get("seccion", "")
    if tipo_actual not in tipos_validos:
        tipo_actual = ""
    if seccion_actual not in secciones_validas:
        seccion_actual = ""

    pagina = request.args.get("page", 1, type=int)
    offset = calcular_offset(pagina, DEFAULT_API_LIMIT)

    params = {"limit": DEFAULT_API_LIMIT, "offset": offset}
    if tipo_actual:
        params["tipo"] = tipo_actual
    if seccion_actual:
        params["seccion"] = seccion_actual
    
    resultado = obtener_articulos_paginados(params=params)
    articulos = resultado.get("datos", [])
    pagination = adaptar_pagination_hateoas(resultado)

    return render_template(
        "public/catalogo.html",
        articulos=articulos,
        pagination=pagination,
        tipos=tipos,
        secciones=secciones,
        tipo_actual=tipo_actual,
        seccion_actual=seccion_actual,
        iconos_tipo=articulos_servicio.ICONOS_TIPO_ARTICULO,
    )


@public_bp.route("/faq", methods=["GET"])
def mostrar_faq():
    """Descripción: función mostrar_faq."""
    return render_template("public/faq.html")


@public_bp.route("/articulos/<int:articulo_id>")
def get_article_details(articulo_id):
    """Muestra el detalle público de un artículo."""
    articulo, fetch_error = articulos_servicio.obtener_articulo(articulo_id)

    return render_template(
        "public/article_details.html", articulo=articulo, fetch_error=fetch_error
    )


@public_bp.app_errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404


@public_bp.app_errorhandler(500)
def error_interno(e):
    return render_template("500.html"), 500

