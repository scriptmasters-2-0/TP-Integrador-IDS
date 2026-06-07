"""Rutas del area de alumnos."""

import logging

from flask import Blueprint, redirect, render_template, request, session, url_for

from services.api_client import (
    get_json,
    obtener_detalle_prestamo,
    obtener_perfil_usuario,
    post_json,
)

logger = logging.getLogger(__name__)
alumno_bp = Blueprint("alumno", __name__, url_prefix="/alumno")
BACKEND_URL = "http://127.0.0.1:5001"


@alumno_bp.route("/perfil")
def perfil():
    """Renderiza la página de perfil del alumno."""
    try:
        usuario = obtener_perfil_usuario()
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        usuario = None

    return render_template("alumno/perfil.html", usuario=usuario)


@alumno_bp.route("/historial")
def historial():
    """Renderiza el historial de préstamos del alumno."""
    token = session.get("token")
    user_id = (session.get("user") or {}).get("id")

    historial_datos = []
    error = None
    if user_id:
        payload, error = get_json(f"/api/users/{user_id}/loans", token=token)
        if isinstance(payload, list):
            for prestamo in payload:
                historial_datos.append(
                    {
                        "fecha": prestamo.get("fecha_retiro", "Desconocida"),
                        "nombre_equipo": prestamo.get("nombre_art", "Artículo"),
                        "id_equipo": prestamo.get("id_reservado"),
                        "sede": prestamo.get("seccion", "Sede FIUBA"),
                        "estado_texto": prestamo.get("estado_reserva", "Pendiente"),
                        "estado_clase": (
                            "badge-warning"
                            if prestamo.get("estado_reserva") == "pendiente"
                            else "badge-success"
                        ),
                    }
                )

    return render_template(
        "alumno/historial.html", historial=historial_datos, fetch_error=error
    )


@alumno_bp.route("/mis-reservas/nueva", methods=["GET", "POST"])
def nueva_reserva():
    """Renderiza y procesa el formulario de nueva reserva para alumnos."""
    token = session.get("token")
    user_id = (session.get("user") or {}).get("id")

    if request.method == "POST":
        item_id = request.form.get("articulo_id")
        if user_id and item_id:
            post_json(
                "/api/loans",
                {"user_id": user_id, "item_id": item_id},
                token=token,
            )
        return redirect(url_for("alumno.historial"))

    items_payload, fetch_error = get_json("/api/items", token=token)
    items = items_payload if isinstance(items_payload, list) else []

    return render_template(
        "alumno/nueva_reserva.html",
        items=items,
        fetch_error=fetch_error,
    )


@alumno_bp.route("/prestamos/<int:id>/comprobante")
def comprobante(id):
    """Renderiza el comprobante de un préstamo específico para el alumno."""
    try:
        datos_api = obtener_detalle_prestamo(id)
        prestamo = {
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
        logger.error(f"Error retrieving loan detail for ID {id}: {e}")
        prestamo = {
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

    return render_template("alumno/comprobante.html", prestamo=prestamo)


@alumno_bp.route("/prestamos/id/comprobante")
def comprobante_sin_id():
    """Renderiza el comprobante de un prestamo especifico para el alumno (sin id)."""
    return render_template("alumno/comprobante.html")


# TODO: Implement POST handlers for profile management
# These handlers are placeholders for features to be implemented:
# - @alumno_bp.route("/perfil/cambiar-contrasena", methods=["POST"]) - Change password
# - @alumno_bp.route("/perfil/solicitar-correccion", methods=["POST"]) - Request data correction
# Currently, these buttons are disabled in the template (alumno/perfil.html)
# Backend endpoints in /api/users/*/password and /api/users/*/corrections should be created


@alumno_bp.route("/dashboard")
def dashboard():
    """Panel principal: reservas activas, score, alertas de penalización."""
    token = session.get("token")
    user = session.get("user")

    if not token or not user:
        return redirect(url_for("public.login"))

    dashboard_data, error = get_json(
        f"/api/alumno/dashboard/{user.get('id')}", token=token
    )

    return render_template(
        "alumno/dashboard.html", dashboard=dashboard_data or {}, fetch_error=error
    )


@alumno_bp.route("/prestamos/<int:id>", methods=["GET"])
def prestamo_detalle(id):
    """Detalle de reserva: estado, fecha retiro/regreso, QR."""
    token = session.get("token")
    if not token:
        return redirect(url_for("public.login"))

    datos_api, error = get_json(f"/api/loans/{id}", token=token)

    if error:
        return render_template(
            "alumno/prestamo_detalle_alumno.html", prestamo=None, fetch_error=error
        )

    prestamo = {
        "id": datos_api.get("id"),
        "estado": datos_api.get("estado_reserva"),
        "fecha_retiro": datos_api.get("fecha_retiro"),
        "fecha_regreso": datos_api.get("fecha_regreso"),
        "qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=FIUBA-RES-{datos_api.get('id')}",
    }

    return render_template("alumno/prestamo_detalle_alumno.html", prestamo=prestamo)
