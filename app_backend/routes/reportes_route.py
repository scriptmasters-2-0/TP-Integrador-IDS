"""Rutas para los endpoints de reportes.

Define los endpoints para obtener reportes del estado del inventario
y de las reservas realizadas en el sistema.
"""

from flask import Blueprint, jsonify, request

from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_OK,
)
from paginacion import construir_respuesta_paginada, obtener_parametros_paginacion
from utiles.autenticacion import requiere_auth
from utiles.servicios import obtener_reporte_db

reportes_bp = Blueprint("reportes", __name__)


@reportes_bp.route("/api/reports", methods=["GET"])
@requiere_auth(roles=["admin", "bibliotecario"])
def obtener_reportes():
    """Obtiene el reporte solicitado según el tipo especificado.

    Returns:
        tuple: JSON con el reporte solicitado y el código HTTP correspondiente.

    """
    tipo = request.args.get("type")
    formato = request.args.get("format")

    tipos_validos = ["pendientes", "devueltos", "atrasados", "todos", "carreras", "articulos"]

    if tipo not in tipos_validos:
        return jsonify({"error": "Tipo de reporte inválido"}), HTTP_BAD_REQUEST

    pagination, error = obtener_parametros_paginacion(request.args)
    if error:
        return jsonify({"error": error}), HTTP_BAD_REQUEST

    reporte_datos, total, error = obtener_reporte_db(
        tipo,
        pagination["limit"],
        pagination["offset"],
    )
    if error:
        return jsonify({"error": error}), HTTP_INTERNAL_SERVER_ERROR

    respuesta = construir_respuesta_paginada(
        reporte_datos,
        total,
        request,
        pagination["limit"],
        pagination["offset"],
    )
    respuesta["tipo_reporte"] = tipo
    respuesta["formato_solicitado"] = formato

    return jsonify(respuesta), HTTP_OK
