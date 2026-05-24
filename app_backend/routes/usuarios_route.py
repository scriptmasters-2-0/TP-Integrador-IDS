from flask import Blueprint, jsonify
from database import obtener_conexion
from http_codes_and_messages import (
    HTTP_NOT_FOUND,
    HTTP_OK,
    HTTP_INTERNAL_SERVER_ERROR,
    MSG_DB_CONNECTION_FAILED,
    MSG_NOT_FOUND,
    MSG_INTERNAL_SERVER_ERROR,
)

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/api/users/<int:user_id>/loans", methods=["GET"])
def get_user_loans(user_id):

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)

        sql_query = """
            SELECT r.id,
                   r.id_reservado,
                   a.nombre_art AS nombre_articulo,
                   r.estado_reserva,
                   r.fecha_retiro,
                   r.fecha_regreso
            FROM reserva r
            LEFT JOIN articulos a ON r.id_reservado = a.id
            WHERE r.id_usuario = %(user_id)s
            ORDER BY r.fecha_retiro DESC
        """
        values = {"user_id": user_id}

        cursor.execute(sql_query, values)
        loans = cursor.fetchall()

        if len(loans) == 0:
            return (
                jsonify({"message": MSG_NOT_FOUND}),
                HTTP_NOT_FOUND,
            )

        return jsonify(loans), HTTP_OK

    except Exception:
        return (
            jsonify({"error": MSG_INTERNAL_SERVER_ERROR}),
            HTTP_INTERNAL_SERVER_ERROR,
        )

    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
