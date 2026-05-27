"""Routes for loan endpoints."""

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
    """Format database loan rows as API responses."""
    return {
        "id": row.get("id"),
        "id_usuario": row.get("id_usuario"),
        "id_reservado": row.get("id_reservado"),
        "estado_reserva": row.get("estado_reserva"),
        "fecha_retiro": (
            row.get("fecha_retiro").isoformat() if row.get("fecha_retiro") else None
        ),
        "fecha_regreso": (
            row.get("fecha_regreso").isoformat() if row.get("fecha_regreso") else None
        ),
    }


@loans_bp.route("/api/loans/<int:loan_id>/status", methods=["PATCH"])
def patch_loan_status(loan_id):  # noqa: PLR0911
    """Update loan status."""
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
