"""Rutas del area de administracion."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from services.api_client import get_json, post_json


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/prestamos/id", methods=["GET", "POST"])
def prestamo_detalle():
    """Renderiza y procesa la vista de detalle de prestamo para administradores."""
    return render_template("admin/prestamo_detalle.html", loan_detail=None)


@admin_bp.route("/articulos")
def listar_articulos():
    """Renderiza la vista de listado de artículos para administradores."""
    token = session.get("token")
    articulos, error = get_json("/api/items", token=token)
    return render_template(
        "admin/articulos.html",
        articulos=articulos if isinstance(articulos, list) else [],
        fetch_error=error,
    )


@admin_bp.route("/articulos/nuevo")
def crear_articulo():
    """Renderiza la vista de creación de nuevo artículo para administradores."""
    return render_template(
        "admin/articulos_form.html",
        articulo=None,
        form_error=request.args.get("error"),
        form_success=request.args.get("success"),
    )


@admin_bp.route("/articulos/guardar", methods=["POST"])
def guardar_articulo():
    """Crea un artículo consumiendo el endpoint backend /api/items."""
    token = session.get("token")
    payload = {
        "nombre_art": request.form.get("nombre"),
        "tipo": request.form.get("tipo"),
        "seccion": request.form.get("seccion"),
        "prestacion_maxima": 7,
        "stock": int(request.form.get("stock") or 1),
        "necesita_reparacion": False,
    }

    _, error, _ = post_json("/api/items", payload, token=token)

    if error:
        return redirect(url_for("admin.crear_articulo", error=error))

    return redirect(url_for("admin.crear_articulo", success="Artículo creado correctamente"))


@admin_bp.route("/dashboard")
def dashboard():
    """Renderiza la vista del dashboard para administradores."""
    # En una implementación real:
    # metrics = requests.get(f"{BACKEND_URL}/reports?type=dashboard").json()
    return render_template("admin/dashboard.html")


@admin_bp.route("/usuarios")
def usuarios():
    """Renderiza la vista de gestión de usuarios para administradores."""
    token = session.get("token")
    usuarios, error = get_json("/api/user", token=token)
    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios if isinstance(usuarios, list) else [],
        fetch_error=error,
    )


@admin_bp.route("/reportes/morosidad")
def reporte_morosidad():
    """Renderiza la vista de reporte de morosidad para administradores."""
    token = session.get("token")
    penalties, error = get_json("/api/penalties", token=token)

    rows = []
    if isinstance(penalties, list):
        for penalty in penalties:
            rows.append(
                {
                    "usuario": penalty.get("id_usuario") or penalty.get("userId"),
                    "articulo": penalty.get("id_reserva") or penalty.get("loanId"),
                    "vencimiento": penalty.get("fecha_fin") or penalty.get("resolvedAt"),
                    "estado": "Activa" if penalty.get("activa", True) else "Levantada",
                }
            )

    return render_template("admin/morosidad.html", penalties=rows, fetch_error=error)

