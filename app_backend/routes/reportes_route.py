"""Rutas para los endpoints de reportes.

Define los endpoints para obtener reportes del estado del inventario
y de las reservas realizadas en el sistema.
"""

from flask import Blueprint, jsonify, request

from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_OK,
)

reportes_bp = Blueprint("reportes", __name__)


def obtener_reporte_db(tipo_reporte):
    """Obtiene los datos del reporte solicitado desde la base de datos.

    Args:
        tipo_reporte (str): El tipo de reporte a obtener
            ('pending', 'returned', 'overdue', 'all', 'careers').

    Returns:
        list[dict]: Lista de diccionarios con los datos obtenidos de la BD.

    """
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    resultado = []

    if tipo_reporte == "overdue":
        cursor.execute("""
            SELECT
                usuario.nombre,
                articulos.nombre_art,
                estado_devuelto.dias_retraso,
                estado_devuelto.condiciones
            FROM estado_devuelto
            JOIN reserva
                ON estado_devuelto.id_reserva = reserva.id
            JOIN usuario
                ON reserva.id_usuario = usuario.id
            JOIN articulos
                ON reserva.id_reservado = articulos.id
            WHERE estado_devuelto.dias_retraso > 0
            """)

    elif tipo_reporte == "pending":
        cursor.execute("""
            SELECT
                reserva.id,
                usuario.nombre,
                articulos.nombre_art,
                reserva.estado_reserva
            FROM reserva
            JOIN usuario
                ON reserva.id_usuario = usuario.id
            JOIN articulos
                ON reserva.id_reservado = articulos.id
            WHERE reserva.estado_reserva = 'pendiente'
            """)

    elif tipo_reporte == "returned":
        cursor.execute("""
            SELECT
                reserva.id,
                usuario.nombre,
                articulos.nombre_art,
                reserva.estado_reserva
            FROM reserva
            JOIN usuario
                ON reserva.id_usuario = usuario.id
            JOIN articulos
                ON reserva.id_reservado = articulos.id
            WHERE reserva.estado_reserva = 'devuelto'
            """)

    elif tipo_reporte == "all":
        cursor.execute("""
            SELECT
                reserva.id,
                usuario.nombre,
                articulos.nombre_art,
                reserva.estado_reserva
            FROM reserva
            JOIN usuario
                ON reserva.id_usuario = usuario.id
            JOIN articulos
                ON reserva.id_reservado = articulos.id
            """)

    elif tipo_reporte == "careers":
        cursor.execute("""
            SELECT
                usuario.carrera,
                COUNT(*) AS cantidad_reservas
            FROM reserva
            JOIN usuario
                ON reserva.id_usuario = usuario.id
            GROUP BY usuario.carrera
            ORDER BY cantidad_reservas DESC
        """)

    elif tipo_reporte == "articles":
        cursor.execute("""
            SELECT
                articulos.nombre_art,
                COUNT(reserva.id) AS cantidad_reservas
            FROM reserva
            JOIN articulos
                ON reserva.id_reservado = articulos.id
            GROUP BY articulos.nombre_art
            ORDER BY cantidad_reservas DESC
        """)

    for fila in cursor:
        resultado.append(fila)

    cursor.close()
    conexion.close()

    return resultado


@reportes_bp.route("/api/reports", methods=["GET"])
def obtener_reportes():
    """Obtiene el reporte solicitado según el tipo especificado.

    Returns:
        tuple: JSON con el reporte solicitado y el código HTTP correspondiente.

    """
    tipo = request.args.get("type")
    formato = request.args.get("format")

    tipos_validos = ["pending", "returned", "overdue", "all", "careers", "articles"]

    if tipo not in tipos_validos:
        return jsonify({"error": "Tipo de reporte inválido"}), HTTP_BAD_REQUEST

    reporte_datos = obtener_reporte_db(tipo)

    respuesta = {
        "tipo_reporte": tipo,
        "formato_solicitado": formato,
        "datos": reporte_datos,
    }

    return jsonify(respuesta), HTTP_OK
