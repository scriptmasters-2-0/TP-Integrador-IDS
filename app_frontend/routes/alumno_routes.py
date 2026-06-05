"""Rutas del area de alumnos."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from services.api_client import (
    get_json,
    post_json,
    obtener_perfil_usuario,
    obtener_detalle_prestamo,
)


alumno_bp = Blueprint("alumno", __name__, url_prefix="/alumno")


@alumno_bp.route("/perfil")
def perfil():
    """Renderiza la página de perfil del alumno."""
    try:
        usuario = obtener_perfil_usuario()
    except Exception:
        usuario = {
            "nombre": "Juan Pérez (Mock)",
            "email": "jperez@fi.uba.ar",
            "legajo": "102345",
            "rol": "alumno",
            "carrera": "Ingeniería Informática",
        }

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
                        "estado_clase": "badge-warning" if prestamo.get("estado_reserva") == "pendiente" else "badge-success",
                    }
                )

    return render_template("alumno/historial.html", historial=historial_datos, fetch_error=error)


@alumno_bp.route("/mis-reservas/nueva", methods=["GET", "POST"])
def nueva_reserva():
    """Renderiza y procesa el formulario de nueva reserva para alumnos."""
    token = session.get("token")
    user_id = (session.get("user") or {}).get("id")

    if request.method == "POST":
        item_id = request.form.get("articulo")
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
    except Exception:
        prestamo = {
            "id": id,
            "estado_texto": "Aprobado (Listo para retirar)",
            "estado_clase": "status-active",
            "equipo_nombre": "Proyector Epson WXGA",
            "equipo_id": "PRJ-012",
            "sede": "Paseo Colón - Aula 204",
            "fecha_reserva": "15 May 2026 - 14:00 hs",
            "fecha_retiro": "15 May 2026 - 15:00 hs",
            "fecha_limite": "15 May 2026 - 18:00 hs",
            "titular_nombre": "Juan Pérez",
            "titular_legajo": "102345",
        }

    return render_template("alumno/comprobante.html", prestamo=prestamo)
