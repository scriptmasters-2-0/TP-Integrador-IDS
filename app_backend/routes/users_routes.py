"""Routes for user and penalty endpoints."""

import mysql.connector
from flask import Blueprint, jsonify, request
from database import obtener_conexion

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_SERVER_ERROR = 500

MSG_BAD_REQUEST = "Invalid request data"
MSG_NOT_FOUND = "Resource not found"
MSG_DB_CONNECTION_FAILED = "Database connection failed"
MSG_INTERNAL_SERVER_ERROR = "An internal server error occurred"

users_bp = Blueprint("users", __name__)


def valid_id(identifier):
    """Validate that the ID is a positive integer."""
    if isinstance(identifier, int) and identifier > 0:
        return identifier
    return None


def format_user(row):
    """Format database user rows as API responses."""
    return {
        "id": row.get("id"),
        "nombre": row.get("nombre"),
        "mail": row.get("mail"),
        "score": row.get("score"),
        "rol": row.get("rol"),
        "carrera": row.get("carrera"),
    }


def format_penalty(row):
    """Format database penalty rows as API responses."""
    return {
        "id": row.get("id"),
        "id_usuario": row.get("id_usuario"),
        "motivo": row.get("motivo"),
        "fecha_inicio": row.get("fecha_inicio").isoformat() if row.get("fecha_inicio") else None,
        "fecha_fin": row.get("fecha_fin").isoformat() if row.get("fecha_fin") else None,
        "activa": bool(row.get("activa")),
    }


@users_bp.route("/api/users", methods=["GET"])
def get_users():
    """Return all users registered in the system."""
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    sql = "SELECT id, nombre, mail, score, rol, carrera FROM usuario ORDER BY id"
    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        users = [format_user(row) for row in cursor.fetchall()]

        return jsonify(users), HTTP_OK

    except mysql.connector.Error:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@users_bp.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Return a specific user by its ID."""
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    if valid_id(user_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    sql = "SELECT id, nombre, mail, score, rol, carrera FROM usuario WHERE id = %(user_id)s"
    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, {"user_id": user_id})
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        return jsonify(format_user(user)), HTTP_OK

    except mysql.connector.Error:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@users_bp.route("/api/users/<int:user_id>/penalties", methods=["GET"])
def get_user_penalties(user_id):
    """Return all penalties associated with a specific user."""
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    if valid_id(user_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    sql = """
        SELECT id, id_usuario, motivo, fecha_inicio, fecha_fin, activa 
        FROM penalizacion 
        WHERE id_usuario = %(user_id)s
        ORDER BY id
    """
    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, {"user_id": user_id})
        penalties = [format_penalty(row) for row in cursor.fetchall()]

        return jsonify(penalties), HTTP_OK

    except mysql.connector.Error:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()