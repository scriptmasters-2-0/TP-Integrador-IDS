"""Rutas del area de alumnos."""

import logging

from flask import Blueprint, redirect, render_template, request, session, url_for

from servicios.api_client import (
    get_json,
    obtener_detalle_reserva,
    obtener_perfil_usuario,
    post_json,
)

logger = logging.getLogger(__name__)
alumno_bp = Blueprint("alumno", __name__, url_prefix="/alumno")


@alumno_bp.route("/perfil")
def perfil():
    """Renderiza la página de perfil del alumno."""
    try:
        usuario = obtener_perfil_usuario()
    except Exception as e:
        logger.error(f"Error fetching usuario profile: {e}")
        usuario = None

    return render_template("alumno/perfil.html", usuario=usuario)


@alumno_bp.route("/historial")
def historial():
    """Renderiza el historial de préstamos del alumno."""
    token = session.get("token")
    usuario_id = (session.get("usuario") or {}).get("id")

    historial_datos = []
    error = None
    if usuario_id:
        payload, error = get_json(f"/usuarios/{usuario_id}/reservas", token=token)
        if isinstance(payload, list):
            for reserva in payload:
                historial_datos.append(
                    {
                        "fecha": reserva.get("fecha_retiro", "Desconocida"),
                        "nombre_equipo": reserva.get("nombre_art", "Artículo"),
                        "id_equipo": reserva.get("id_reservado"),
                        "sede": reserva.get("seccion", "Sede FIUBA"),
                        "estado_texto": reserva.get("estado_reserva", "Pendiente"),
                        "estado_clase": (
                            "badge-warning" if reserva.get("estado_reserva") == "pendiente" else "badge-exito"
                        ),
                    }
                )

    return render_template("alumno/historial.html", historial=historial_datos, fetch_error=error)


@alumno_bp.route("/mis-reservas/nueva", methods=["GET", "POST"])
def nueva_reserva():
    """Renderiza y procesa el formulario de nueva reserva para alumnos."""
    token = session.get("token")
    usuario_id = (session.get("usuario") or {}).get("id")

    if request.method == "POST":
        articulo_id = request.form.get("articulo_id")
        if usuario_id and articulo_id:
            post_json(
                "/reservas",
                {"usuario_id": usuario_id, "articulo_id": articulo_id},
                token=token,
            )
        return redirect(url_for("alumno.historial"))

    articulos_payload, fetch_error = get_json("/articulos", token=token)
    articulos = articulos_payload if isinstance(articulos_payload, list) else []

    return render_template(
        "alumno/nueva_reserva.html",
        articulos=articulos,
        fetch_error=fetch_error,
    )


@alumno_bp.route("/reservas/<int:id>/comprobante")
def comprobante(id):
    """Renderiza el comprobante de un préstamo específico para el alumno."""
    try:
        datos_api = obtener_detalle_reserva(id)
        reserva = {
            "id": datos_api.get("id", id),
            "estado_texto": datos_api.get("estado_reserva", "Pendiente"),
            "estado_clase": "status-active",
            "equipo_nombre": datos_api.get("nombre_art", "Material no especificado"),
            "equipo_id": datos_api.get("id_reservado", "N/A"),
            "sede": datos_api.get("seccion", "Sede Central FIUBA"),
            "fecha_reserva": datos_api.get("fecha_retiro", "N/A"),
            "fecha_retiro": datos_api.get("fecha_retiro", "N/A"),
            "fecha_limite": datos_api.get("fecha_regreso", "N/A"),
            "titular_nombre": datos_api.get("nombre", "Alumno"),
            "titular_legajo": datos_api.get("id_usuario", "N/A"),
        }
    except Exception as e:
        logger.error(f"Error retrieving reserva detail for ID {id}: {e}")
        reserva = {
            "id": id,
            "estado_texto": "Error al cargar",
            "estado_clase": "status-error",
            "equipo_nombre": "No disponible",
            "equipo_id": "N/A",
            "sede": "No especificada",
            "fecha_reserva": "N/A",
            "fecha_retiro": "N/A",
            "fecha_limite": "N/A",
            "titular_nombre": "Usuario",
            "titular_legajo": "N/A",
        }

    return render_template("alumno/comprobante.html", reserva=reserva)


@alumno_bp.route("/reservas/id/comprobante")
def comprobante_sin_id():
    """Renderiza el comprobante de un reserva especifico para el alumno (sin id)."""
    return render_template("alumno/comprobante.html")


# TODO: Implement POST handlers for profile management
# These handlers are placeholders for features to be implemented:
# - @alumno_bp.route("/perfil/cambiar-contrasena", methods=["POST"]) - Change contrasenia
# - @alumno_bp.route("/perfil/solicitar-correccion", methods=["POST"]) - Request data correction
# Currently, these buttons are disabled in the template (alumno/perfil.html)
# Backend endpoints in /api/usuarios/*/contrasenia and /api/usuarios/*/corrections should be created


@alumno_bp.route("/dashboard")
def dashboard():
    """Panel principal: reservas activas, puntaje, alertas de penalización."""
    token = session.get("token")
    usuario = session.get("usuario")

    if not token or not usuario:
        return redirect(url_for("public.login"))

    dashboard_data, error = get_json(f"/alumno/dashboard/{usuario.get('id')}", token=token)

    return render_template("alumno/dashboard.html", dashboard=dashboard_data or {}, fetch_error=error)


@alumno_bp.route("/reservas/<int:id>", methods=["GET"])
def reserva_detalle(id):
    """Detalle de reserva: estado, fecha retiro/regreso, QR."""
    token = session.get("token")
    if not token:
        return redirect(url_for("public.login"))

    datos_api, error = get_json(f"/reservas/{id}", token=token)

    if error:
        return render_template("alumno/reserva_detalle_alumno.html", reserva=None, fetch_error=error)

    reserva = {
        "id": datos_api.get("id"),
        "estado": datos_api.get("estado_reserva"),
        "fecha_retiro": datos_api.get("fecha_retiro"),
        "fecha_regreso": datos_api.get("fecha_regreso"),
        "qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=FIUBA-RES-{datos_api.get('id')}",
    }

    return render_template("alumno/reserva_detalle_alumno.html", reserva=reserva)
