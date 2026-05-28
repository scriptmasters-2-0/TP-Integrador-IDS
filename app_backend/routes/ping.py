"""Ruta de verificación de estado del servidor (health check).

Provee un endpoint simple para verificar que el servidor está
activo y respondiendo correctamente.
"""

from flask import Blueprint, jsonify

from http_codes_and_messages import HTTP_OK

ping_bp = Blueprint("ping", __name__)


@ping_bp.route("/ping", methods=["GET"])
def ping():
    """Verifica que el servidor está activo.

    Returns:
        tuple: Respuesta JSON con el mensaje 'pong' y código HTTP 200.

    """
    return jsonify({"message": "pong"}), HTTP_OK
