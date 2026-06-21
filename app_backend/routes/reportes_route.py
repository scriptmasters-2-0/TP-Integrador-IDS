"""Rutas para los endpoints de reportes.

Define los endpoints para obtener reportes del estado del inventario
y de las reservas realizadas en el sistema.
"""

from flask import Blueprint, jsonify, request

from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_OK,
    MSG_DB_CONNECTION_FAILED,
)
from paginacion import construir_respuesta_paginada, obtener_parametros_paginacion
from routes.auth_route import requiere_auth

reportes_bp = Blueprint("reportes", __name__)


def obtener_sql_reporte(tipo_reporte):
    """Devuelve la consulta base del reporte solicitado."""
    consultas = {
        "atrasados": """
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
        """,
        "pendientes": """
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
        """,
        "devueltos": """
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
        """,
        "todos": """
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
        """,
        "carreras": """
            SELECT
                usuario.carrera,
                COUNT(*) AS cantidad_reservas
            FROM reserva
            JOIN usuario
                ON reserva.id_usuario = usuario.id
            GROUP BY usuario.carrera
            ORDER BY cantidad_reservas DESC
        """,
        "articulos": """
            SELECT
                articulos.nombre_art,
                COUNT(reserva.id) AS cantidad_reservas
            FROM reserva
            JOIN articulos
                ON reserva.id_reservado = articulos.id
            GROUP BY articulos.nombre_art
            ORDER BY cantidad_reservas DESC
        """,
    }
    return consultas.get(tipo_reporte)


def obtener_reporte_db(tipo_reporte, limit, offset):
    """Obtiene los datos paginados del reporte solicitado desde la base de datos.

    Args:
        tipo_reporte (str): El tipo de reporte a obtener
            ('pendientes', 'devueltos', 'atrasados', 'todos', 'carreras', 'articulos').
        limit (int): Cantidad máxima de registros.
        offset (int): Posición inicial de registros.

    Returns:
        tuple: Datos, total y error de conexión si corresponde.

    """
    conn = obtener_conexion()
    if conn is None:
        return None, None, MSG_DB_CONNECTION_FAILED

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)

        sql_base = obtener_sql_reporte(tipo_reporte)
        cursor.execute(f"SELECT COUNT(*) AS total FROM ({sql_base}) AS reporte")
        total = cursor.fetchone()["total"]

        cursor.execute(
            f"""
            {sql_base}
            LIMIT %(limit)s OFFSET %(offset)s
            """,
            {"limit": limit, "offset": offset},
        )
        resultado = list(cursor)

        return resultado, total, None
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


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
