from flask import Blueprint, jsonify, request
from flask_login import login_required
from http_codes_and_messages import (
    HTTP_OK,
    HTTP_BAD_REQUEST,
)
from database import obtener_conexion

blueprint_reportes = Blueprint("reportes", __name__)


# pre: tipo_reporte es un string válido ("pending", "returned", "overdue", "all").
# post: obtiene datos del reporte solicitado desde la base de datos usando un bucle.
def obtener_reporte_db(tipo_reporte):
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

    for fila in cursor:
        resultado.append(fila)

    cursor.close()
    conexion.close()

    return resultado


# pre: el usuario está autenticado y envía un tipo de reporte válido en la URL.
# post: retorna el reporte solicitado en formato JSON.
@blueprint_reportes.route("/api/reports", methods=["GET"])
@login_required
def obtener_reportes():
    tipo = request.args.get("type")
    formato = request.args.get("format")

    tipos_validos = ["pending", "returned", "overdue", "all"]

    if tipo not in tipos_validos:
        return jsonify({"error": "Tipo de reporte inválido"}), HTTP_BAD_REQUEST

    reporte_datos = obtener_reporte_db(tipo)

    respuesta = {
        "tipo_reporte": tipo,
        "formato_solicitado": formato,
        "datos": reporte_datos,
    }

    return jsonify(respuesta), HTTP_OK
