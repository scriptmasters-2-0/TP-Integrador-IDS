"""Rutas para los endpoints de préstamos."""

import mysql.connector
from flask import Blueprint, jsonify, request

from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
    MSG_BAD_REQUEST,
    MSG_DB_CONNECTION_FAILED,
    MSG_INTERNAL_SERVER_ERROR,
    MSG_NOT_FOUND,
)
from validators import valid_id, valid_loan_status_update

loans_bp = Blueprint("loans", __name__)


def format_loan(row):
    """Formatea una fila de préstamo de la base de datos como respuesta de la API.

    Convierte los campos de fecha a formato ISO 8601 cuando están presentes.

    Args:
        row (dict): Diccionario con los datos del préstamo obtenidos de la
            base de datos.

    Returns:
        dict: Diccionario formateado con los campos del préstamo para la respuesta.

    """
    return {
        "id": row.get("id"),
        "id_usuario": row.get("id_usuario"),
        "id_reservado": row.get("id_reservado"),
        "estado_reserva": row.get("estado_reserva"),
        "fecha_retiro": (row.get("fecha_retiro").isoformat() if row.get("fecha_retiro") else None),
        "fecha_regreso": (row.get("fecha_regreso").isoformat() if row.get("fecha_regreso") else None),
    }


@loans_bp.route("/api/loans/<int:loan_id>/status", methods=["PATCH"])
def patch_loan_status(loan_id):  # noqa: PLR0911
    """Actualiza el estado de un préstamo.

    Recibe el ID del préstamo como parámetro de ruta y el nuevo estado
    en el cuerpo de la petición como JSON.

    Args:
        loan_id (int): Identificador único del préstamo a actualizar.

    Returns:
        tuple: JSON con el préstamo actualizado y el código HTTP correspondiente.

    """
    if valid_id(loan_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    try:
        data = request.get_json()
    except Exception:
        data = None

    is_valid, error = valid_loan_status_update(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            UPDATE reserva
            SET estado_reserva = %(estado_reserva)s
            WHERE id = %(loan_id)s
            """,
            {
                "estado_reserva": data.get("estado_reserva"),
                "loan_id": loan_id,
            },
        )
        conn.commit()

        cursor.execute(
            """
            SELECT id,
                   id_usuario,
                   id_reservado,
                   estado_reserva,
                   fecha_retiro,
                   fecha_regreso
            FROM reserva
            WHERE id = %(loan_id)s
            """,
            {"loan_id": loan_id},
        )
        loan = cursor.fetchone()

        if not loan:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        return jsonify(format_loan(loan)), HTTP_OK

    except mysql.connector.Error:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

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


def obtener_detalle_prestamo_db(loan_id):
    """Obtiene el detalle completo de un préstamo.

    Args:
        loan_id (int): Identificador único del préstamo a consultar.

    Returns:
        tuple: JSON con el detalle del préstamo y el código HTTP correspondiente.

    """
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


@loans_bp.route("/api/loans/<int:loan_id>", methods=["GET"])
def obtener_detalle_prestamo(loan_id):
    """Obtiene el detalle completo de un préstamo.

    Args:
        loan_id (int): Identificador único del préstamo a consultar.

    Returns:
        tuple: JSON con el detalle del préstamo y el código HTTP correspondiente.

    """
    if loan_id <= 0:
        return jsonify({"error": "ID inválido"}), HTTP_BAD_REQUEST

    resultado = obtener_detalle_prestamo_db(loan_id)

    if resultado is not None:
        return jsonify(resultado), HTTP_OK

    else:
        return jsonify({"error": "Préstamo no encontrado"}), HTTP_NOT_FOUND
