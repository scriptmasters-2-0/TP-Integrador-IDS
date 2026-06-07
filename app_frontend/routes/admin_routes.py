"""Rutas del area de administracion."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from services import items_service
from services.api_client import get_json, obtener_detalle_prestamo, post_json
from services.normativas_service import (
    actualizar_normativa,
    crear_normativa,
    eliminar_normativa,
    obtener_normativas,
)
from services.reports_service import obtener_reportes

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/prestamos/<int:id>", methods=["GET", "POST"])
def prestamo_detalle(id):
    """Renderiza y procesa la vista de detalle de préstamo para administradores."""
    if request.method == "POST":
        return redirect(url_for("admin.prestamo_detalle", id=id))

    try:
        datos_api = obtener_detalle_prestamo(id)
        prestamo = {
            "id": datos_api.get("id", id),
            "estado_general": datos_api.get("estado_reserva", "pendiente"),
            "estado_texto": datos_api.get("estado_reserva", "Pendiente"),
            "estado_clase": "status-pending"
            if datos_api.get("estado_reserva") == "pendiente"
            else "status-active",
            "equipo_nombre": datos_api.get("nombre_art", "Material no especificado"),
            "equipo_id": datos_api.get("id_reservado", "N/A"),
            "titular_nombre": datos_api.get("nombre", "Alumno"),
            "titular_legajo": datos_api.get("id_usuario", "N/A"),
            "titular_carrera": datos_api.get("carrera", "No definida"),
            "fecha_retiro": datos_api.get("fecha_retiro", "N/A"),
            "fecha_limite": datos_api.get("fecha_regreso", "N/A"),
        }
    except Exception:
        prestamo = {
            "id": id,
            "estado_general": "en_curso",
            "estado_texto": "En curso (Retirado)",
            "estado_clase": "status-pending",
            "equipo_nombre": "Proyector Epson WXGA",
            "equipo_id": "PRJ-012",
            "titular_nombre": "Juan Pérez",
            "titular_legajo": "102345",
            "titular_carrera": "Ingeniería Informática",
            "fecha_retiro": "15 May 2026 - 15:00 hs",
            "fecha_limite": "15 May 2026 - 18:00 hs",
        }

    return render_template("admin/prestamo_detalle.html", prestamo=prestamo)


@admin_bp.route("/articulos")
def listar_articulos():
    """Renderiza la vista de listado de artículos para administradores."""
    articulos = items_service.obtener_items()

    return render_template(
        "admin/articulos.html",
        articulos=articulos,
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

    return redirect(
        url_for("admin.crear_articulo", success="Artículo creado correctamente")
    )


@admin_bp.route("/dashboard")
def dashboard():
    """Renderiza la vista del dashboard para administradores."""
    return render_template("admin/dashboard.html")


@admin_bp.route("/reportes", methods=["GET"])
def reportes():
    """Renderiza la vista de reportes para administradores."""
    rol = session.get("rol")
    if rol not in ["admin", "bibliotecario"]:
        return redirect("/")

    rta = obtener_reportes("careers")

    carreras = rta.get("datos", [])

    return render_template("admin/reportes.html", carreras=carreras)


@admin_bp.route("/normativas", methods=["GET", "POST"])
def normativas():
    """ABM de normativas solo visibles para admins y bibliotecarios"""

    rol = session.get("rol")
    if rol not in ["admin", "bibliotecario"]:
        return redirect("/")
    
    if request.method == "POST":
        id_normativa = request.form.get("id")
        data = {
            "titulo": request.form.get("titulo"),
            "descripcion": request.form.get("descripcion"),
        }
        if id_normativa:
            actualizar_normativa(id_normativa, data)
        else:
            crear_normativa(data)
        return redirect("/admin/normativas")
    
    normativas = obtener_normativas()
    normativa_editada = None
    id_editar = request.args.get("editar")

    if id_editar:
        for normativa in normativas:
            if str(normativa["id"]) == str(id_editar):
                normativa_editada = normativa
                break
            
    return render_template(
        "admin/normativas.html",
        normativas=normativas,
        normativa_editada=normativa_editada,
    )


@admin_bp.route("/normativas/eliminar", methods=["POST"])
def eliminar_norm():
    id_norm = request.form.get("id")
    eliminar_normativa(id_norm)
    return redirect("/admin/normativas")


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
                    "vencimiento": penalty.get("fecha_fin")
                    or penalty.get("resolvedAt"),
                    "estado": "Activa" if penalty.get("activa", True) else "Levantada",
                }
            )

    return render_template("admin/morosidad.html", penalties=rows, fetch_error=error)
