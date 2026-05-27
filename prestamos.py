from flask import Blueprint, jsonify
from flask_login import login_required
from constants import HTTP_OK, HTTP_NOT_FOUND, HTTP_BAD_REQUEST
from database import obtener_conexion

blueprint_prestamos = Blueprint("prestamos", __name__)


# pre:  loan_id es un entero positivo.
# post: busca el préstamo en la base de datos usando un bucle. Retorna el diccionario si existe, o None si no.
def obtener_detalle_prestamo_db(loan_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT 
            reserva.id, 
            usuario.nombre, 
            articulos.nombre_art, 
            reserva.estado_reserva, 
            reserva.fecha_retiro, 
            reserva.fecha_regreso 
        FROM reserva
        JOIN usuario 
            ON reserva.id_usuario = usuario.id
        JOIN articulos 
            ON reserva.id_reservado = articulos.id
        WHERE reserva.id = %s
        """,
        (loan_id,),
    )

    prestamo = None

    for fila in cursor:
        prestamo = fila

    cursor.close()
    conexion.close()

    return prestamo


# pre:  el usuario está autenticado y loan_id es válido.
# post: retorna los detalles del préstamo si existe. Retorna 404 si no existe. Retorna 400 si el ID es inválido.
@blueprint_prestamos.route("/api/loans/<int:loan_id>", methods=["GET"])
@login_required
def obtener_detalle_prestamo(loan_id):

    if loan_id <= 0:
        return jsonify({"error": "ID inválido"}), HTTP_BAD_REQUEST

    resultado = obtener_detalle_prestamo_db(loan_id)

    if resultado != None:
        return jsonify(resultado), HTTP_OK

    else:
        return jsonify({"error": "Préstamo no encontrado"}), HTTP_NOT_FOUND
