from database import obtener_conexion
from flask import Blueprint, jsonify, request
from validators import valid_user
from http_codes_and_messages import (
    HTTP_NOT_FOUND,
    HTTP_OK,
    HTTP_CREATED,
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_SERVER_ERROR,
    MSG_DB_CONNECTION_FAILED,
    MSG_NOT_FOUND,
    MSG_BAD_REQUEST,
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


@usuarios_bp.route("/api/users", methods=["POST"])
def create_user():

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    try:
        data = request.get_json()
    except Exception:
        data = None

    if not data:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    is_valid, error = valid_user(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    cursor = None

    try:
        cursor = conn.cursor()
        sql = "INSERT INTO usuario (nombre, mail, rol, carrera) VALUES (%(nombre)s, %(mail)s, %(rol)s, %(carrera)s)"
        values = {
            "nombre": f"{data.get('firstName')} {data.get('lastName')}",
            "mail": data.get("email"),
            "rol": data.get("role"),
            "carrera": data.get("career"),
        }
        cursor.execute(sql, values)
        conn.commit()

        user_id = cursor.lastrowid

        user = {
            "id": user_id,
            "username": data.get("username"),
            "email": data.get("email"),
            "firstName": data.get("firstName"),
            "lastName": data.get("lastName"),
            "role": data.get("role"),
            "career": data.get("career"),
            "isActive": True,
        }

        return jsonify(user), HTTP_CREATED

    except Exception:
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            if conn:
                conn.close()
        except Exception:
            pass
