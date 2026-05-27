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
from validators import valid_id, valid_penalty_patch

penalties_bp = Blueprint("penalties", __name__)


# pre: -
# post: devuelve True si el usuario existe en la BD, False caso contrario
def usuario_existe(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM usuario WHERE id = %s", (id_usuario,))
    existe = cursor.fetchone() is not None
    cursor.close()
    conexion.close()
    return existe


# pre:-
# post: devuelve una lista de diccionarios con todas las penalizaciones de la BD.
def listar_penalizaciones_db():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM penalizacion")
    penalizaciones = cursor.fetchall()
    cursor.close()
    conexion.close()
    return penalizaciones


# pre:  id_usuario es entero positivo, motivo es string no vacío.
# post: inserta una penalización activa por 15 días y retorna el ID generado.
def crear_penalizacion_db(id_usuario, motivo):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO penalizacion (id_usuario, motivo, fecha_inicio, fecha_fin, activa)
        VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 15 DAY), TRUE)
        """,
        (id_usuario, motivo),
    )
    conexion.commit()
    id_generado = cursor.lastrowid
    cursor.close()
    conexion.close()
    return id_generado


def format_penalty(row):
    """Format database penalty rows as API responses."""
    return {
        "id": row.get("id"),
        "userId": row.get("id_usuario"),
        "loanId": row.get("id_reserva"),
        "reason": row.get("motivo"),
        "status": "Activa" if row.get("activa") else "Levantada",
        "severity": row.get("severity"),
        "notes": row.get("motivo"),
        "createdAt": (
            row.get("fecha_inicio").isoformat() if row.get("fecha_inicio") else None
        ),
        "resolvedAt": (
            row.get("fecha_fin").isoformat() if row.get("fecha_fin") else None
        ),
    }


# post: devuelve un diccionario con los datos de la penalización si existe, None si no.
def obtener_penalizacion_por_id(id_penalizacion):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM penalizacion WHERE id = %s", (id_penalizacion,))
    penalizacion = cursor.fetchone()
    cursor.close()
    conexion.close()
    return penalizacion


@penalties_bp.route("/api/penalties/<int:penalty_id>", methods=["GET"])
def get_penalty(penalty_id):
    """Return a penalty by id."""
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    if valid_id(penalty_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id,
                   id_usuario,
                   id_reserva,
                   motivo,
                   fecha_inicio,
                   fecha_fin,
                   activa,
                   severity
            FROM penalizacion
            WHERE id = %(penalty_id)s
            """,
            {"penalty_id": penalty_id},
        )
        row = cursor.fetchone()

        if not row:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        return jsonify(format_penalty(row)), HTTP_OK

    except mysql.connector.Error:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    finally:
        try:
            cursor.close()

        except Exception:
            pass

        try:
            conn.close()

        except Exception:
            pass


@penalties_bp.route("/api/penalties/<int:penalty_id>", methods=["PATCH"])
def patch_penalty(penalty_id):
    """Update part of a penalty."""
    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    if valid_id(penalty_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    try:
        data = request.get_json()
    except Exception:
        data = None

    is_valid, error = valid_penalty_patch(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    if "status" in data:
        data.update({"activa": 1 if data.get("status") == "Activa" else 0})
        data.pop("status")

    if "notes" in data:
        data.update({"motivo": data.get("notes")})
        data.pop("notes")

    keysToUpdate = list(data.keys())
    set_expressions = [f"{f} = %({f})s" for f in keysToUpdate]

    if not data.get("activa", True):
        set_expressions.append("fecha_fin = NOW()")

    set_clause = ", ".join(set_expressions)
    data.update({"penalty_id": penalty_id})

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        sql = f"UPDATE penalizacion SET {set_clause} WHERE id = %(penalty_id)s"
        cursor.execute(sql, data)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        cursor.execute(
            """
            SELECT id,
                   id_usuario,
                   id_reserva,
                   motivo,
                   fecha_inicio,
                   fecha_fin,
                   activa,
                   severity
            FROM penalizacion
            WHERE id = %(penalty_id)s
            """,
            {"penalty_id": penalty_id},
        )

        row = cursor.fetchone()

        if not row:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        return jsonify(format_penalty(row)), HTTP_OK

    except mysql.connector.Error:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    finally:
        try:
            cursor.close()

        except Exception:
            pass

        try:
            conn.close()

        except Exception:
            pass


# pre:  el request incluye un JWT válido con rol admin.
# post: retorna 200 con lista de todas las penalizaciones, 403 si no es admin.
@penalties_bp.route("/api/penalties", methods=["GET"])
def listar_penalizaciones():
    penalizaciones = listar_penalizaciones_db()
    return jsonify(penalizaciones), HTTP_OK


# pre:  el request incluye un JWT válido con rol admin y body con 'user_id' y 'reason'.
# post: retorna 201 con la penalización creada, 400 si faltan datos, 404 si el usuario no existe.
@penalties_bp.route("/api/penalties", methods=["POST"])
def crear_penalizacion():
    datos = request.get_json()

    if not datos or not datos.get("user_id") or not datos.get("reason"):
        return jsonify({"error": "user_id y reason son requeridos"}), HTTP_BAD_REQUEST

    id_usuario = datos["user_id"]
    motivo = datos["reason"]

    if not usuario_existe(id_usuario):
        return jsonify({"error": "Usuario no encontrado"}), HTTP_NOT_FOUND

    id_penalizacion = crear_penalizacion_db(id_usuario, motivo)
    penalizacion = obtener_penalizacion_por_id(id_penalizacion)

    return jsonify(penalizacion), HTTP_CREATED
