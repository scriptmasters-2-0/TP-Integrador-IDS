"""Rutas de la API para la generación de códigos QR de reservas.

Define los endpoints para generar y obtener códigos QR asociados
a las reservas del sistema.
"""

from flask import Blueprint, jsonify, request

from http_codes_and_messages import (
    HTTP_FORBIDDEN,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
    MSG_FORBIDDEN,
)
from utiles.autenticacion import requiere_auth
from utiles.qr import construir_contenido_qr, generar_qr
from utiles.servicios import obtener_reserva_por_id

qr_bp = Blueprint("qr", __name__)


@qr_bp.route("/api/qr/reservas/<int:id_reserva>", methods=["GET"])
@requiere_auth(roles=["admin", "profesor", "bibliotecario", "alumno"])
def obtener_qr_reserva(id_reserva):
    """Genera y devuelve el QR correspondiente a una reserva.

    El request debe incluir un JWT válido en el header Authorization.

    Args:
        id_reserva (int): Entero correspondiente a una reserva existente.

    Returns:
        tuple: JSON con id_reserva y qrData (imagen en base64) y código 200,
               o error 404 si no existe la reserva.

    """
    reserva, error = obtener_reserva_por_id(id_reserva)
    if error:
        return jsonify({"error": error}), HTTP_INTERNAL_SERVER_ERROR

    if reserva is None:
        return jsonify({"error": "Reserva no encontrada"}), HTTP_NOT_FOUND

    if request.usuario_rol not in ("admin", "bibliotecario") and reserva.get("id_usuario") != request.usuario_id:
        return jsonify({"error": MSG_FORBIDDEN}), HTTP_FORBIDDEN

    contenido_qr = construir_contenido_qr(reserva)
    imagen_qr = generar_qr(contenido_qr)

    return jsonify({"id_reserva": id_reserva, "qrData": imagen_qr}), HTTP_OK
