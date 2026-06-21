"""Rutas del área del bibliotecario."""

from flask import Blueprint, request, redirect, session, url_for, render_template, jsonify

from http_codes_and_messages import HTTP_FORBIDDEN, MSG_FORBIDDEN
from servicios.reservas_servicio import (
    establecer_estado_reserva,
    obtener_solicitudes,
    escanear_qr_reserva,
)

biblio_bp = Blueprint("biblioteca", __name__, url_prefix="/biblioteca")

@biblio_bp.route("/reservas/solicitudes", methods=["GET"])
def listar_pendientes():
    """Obtiene todas las reservas con estado pendiente."""
    token = session.get("token")
    rol = session.get("rol")
    if not token or rol != "bibliotecario":
        return redirect(url_for("public.login"))

    reservas_pendientes = obtener_solicitudes(token=token)

    return render_template(
        "biblioteca/solicitudes_reservas.html",
        reservas=reservas_pendientes,
        mensaje_error=request.args.get("mensaje_error"),
    )


@biblio_bp.route("/reservas/solicitudes/<int:id_reserva>", methods=["POST"])
def modificar_estado(id_reserva):
    """Acepta o rechaza una solicitud de reserva."""
    token = session.get("token")
    rol = session.get("rol")
    if not token or rol != "bibliotecario":
        return redirect(url_for("public.login"))

    estado_a_modificar = request.form.get("estado_reserva")

    actualizada, error, status = establecer_estado_reserva(
        id_reserva, {"estado_reserva": estado_a_modificar}, token=token
    )
    if error or not actualizada:
        return redirect(
            url_for(
                "biblioteca.listar_pendientes",
                mensaje_error="No se pudo cambiar el estado de la reserva.",
            )
        )

    return redirect(url_for("biblioteca.listar_pendientes"))


@biblio_bp.route("/scan", methods=["GET"])
def abrir_escaner():

    token = session.get("token")
    rol = session.get("rol") 

    if not token or rol != "bibliotecario":
        return redirect(url_for("public.login"))
    
    return render_template("biblioteca/escanear_qr.html")


@biblio_bp.route("/reservas/<int:id_reserva>/scan", methods=["PATCH"])
def escanear_reserva(id_reserva):
    """Escanea una reserva y cambia su estado.
    estado: entregado al escanear por primera vez en el retiro del articulo
    estado: devuelto al escanear por segunda vez en la devolucion"""

    token = session.get("token")
    rol = session.get("rol")

    if not token:
        return redirect(url_for("public.login"))

    if rol != "bibliotecario":
        return jsonify({"error": MSG_FORBIDDEN}), HTTP_FORBIDDEN
    
    escaneo, error = escanear_qr_reserva(id_reserva, token)

    if error:
        return jsonify({"error": error}), 400
    
    return jsonify(escaneo), 200
